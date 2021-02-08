import random
import logging
import os, json
import datetime
import shutil
from urllib.parse import urljoin
from multiprocessing import Pool

from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.template import loader
from django.db import close_old_connections
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from pypinyin import lazy_pinyin

from .forms import ProjectForm, ABTestForm, GitForm, WgetForm, \
    RecordForm, PermissionsForm, FileUploadForm
from .models import Project, Record, ABTest, Git, Wget, RecordLog, \
    Permissions, FileUpload
from assets.models import Service, IDC
from mix_tools.permission import *
from mix_tools.sp_gitpython import git_update, web_dir
from mix_tools.sp_wget import wget
from mix_tools.sp_subprocess import popen, rsync
from mix_tools.check import check_script_type
from mix_tools.sp_paramiko import remote_command
from mix_tools.sp_email import send_email_for_release
from mix_tools.sp_gitlab import retrieve_commits
from .tasks import async_sendmail
from small_platform.settings import FILE_PATH_FIELD_DIRECTORY as script_directory

User = get_user_model()
logger = logging.getLogger('release')

from_email = 'svp.mobileztgame.com <svp@ztgame.com>'

class DeleteBaseView(LoginRequiredMixin, View):
    """删除基础视图"""
    queryset = None

    def post(self, request, *args, **kwargs):
        delete_objects = request.POST.get('delete_objects')
        delete_objects = json.loads(delete_objects)
        if not (len(delete_objects) != 0 or isinstance(delete_objects, list)):
            return JsonResponse({'code': 1, 'msg': '删除失败', 'results': '参数错误'})
        error_list = []
        for item in delete_objects:
            try:
                self.queryset.filter(id=item['id']).delete()
            except Exception as e:
                error_list.append({'name': item['name'], 'errors': str(e)})
        if error_list:
            return JsonResponse({
                'code': 1,
                'msg': '删除失败',
                'results': '\n'.join('* %s' % e for e in error_list)
            })
        else:
            return JsonResponse({
                'code': 0,
                'msg': '删除成功',
                'results': '删除成功'
            })


class ProjectListView(LoginRequiredMixin, AccessOperator, TemplateView):
    """
    项目列表(表格)视图
    """
    template_name = 'release/project_list.html'

    def get_context_data(self, **kwargs):
        kwargs.update(
            project_name=[item[0] for item in Project.objects.values_list('name')]
        )
        return super().get_context_data(**kwargs)


class ProjectCreateView(LoginRequiredMixin, AccessOperator, CreateView):
    """
    项目创建视图
    """
    template_name = 'release/project_create_form.html'
    form_class = ProjectForm
    model = Project

    def get_context_data(self, **kwargs):
        git_form = GitForm(prefix='git_form')
        wget_form = WgetForm(prefix='wget_form')
        abtest_form = ABTestForm(prefix='abtest_form')
        service_qs = Service.objects.all()
        kwargs.update(
            git_form=git_form,
            wget_form=wget_form,
            abtest_form=abtest_form,
            service_qs=service_qs
        )
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            operator = self.request.POST.getlist('operator[]')
            developer = self.request.POST.getlist('developer[]')
            kwargs['data'] = {}
            for k, v in self.request.POST.items():
                kwargs['data'].update({k: v})
            kwargs['data'].update(
                operator=operator,
                developer=developer,
                success='创建成功',
                error='创建失败'
            )
            kwargs['data'].pop('operator[]')
            kwargs['data'].pop('developer[]')
        return kwargs

    def form_valid(self, form):
        form_logs = []
        # 持久化ProjectForm表单
        form_ins = form.save()
        # 持久化GitForm、WgetForm表单
        if form.data['get_code_type'] == 'git':
            form.data['git_form-project'] = form_ins.id
            git_form = GitForm(prefix='git_form', data=form.data)
            if git_form.is_valid():
                git_form.save()
            else:
                form_logs.append(git_form.errors.as_text())
        else:
            form.data['wget_form-project'] = form_ins.id
            wget_form = WgetForm(prefix='wget_form', data=form.data)
            if wget_form.is_valid():
                wget_form.save()
            else:
                form_logs.append(wget_form.errors.as_text())
        # 处理ABTestForm表单
        service_hosts = form_ins.hosts.hosts.all()
        if form.data['abtest_form-mode'] == "0":
            abtest_hosts = []
            for host in service_hosts:
                if host.idc_id == int(form.data['abtest_form-idc']):
                    abtest_hosts.append(host.ip)
        elif form.data['abtest_form-mode'] == "1":
            percent = form.data['abtest_form-percent']
            abtest_hosts = []
            res = round(len(service_hosts) * int(percent) / 100)
            if res < 1:
                abtest_hosts.append(random.choice(service_hosts).ip)
            else:
                for n in range(res):
                    abtest_hosts.append(random.choice(service_hosts).ip)
        else:
            abtest_hosts = self.request.POST.getlist('abtest_form-hosts[]')
        form.data['abtest_form-hosts'] = ','.join(abtest_hosts)
        form.data['abtest_form-project'] = form_ins.id
        abtest_form = ABTestForm(prefix='abtest_form', data=form.data)
        if abtest_form.is_valid():
            abtest_form.save()
        else:
            form_logs.append(abtest_form.errors.as_text())

        if not form_logs:
            return JsonResponse({
                'code': 0,
                'msg': form.data['success'],
                'results': form_ins.name
            })
        else:
            return JsonResponse({
                'code': 1,
                'msg': form.data['error'],
                'results': '\n'.join(form_logs)
            })

    def form_invalid(self, form):
        return JsonResponse({
            'code': 1,
            'msg': form.data['error'],
            'results': form.errors.as_text()
        })


class ProjectUpdateView(LoginRequiredMixin, AccessOperator, UpdateView):
    """
    项目查看、更新视图
    """
    template_name = 'release/project_update_form.html'
    form_class = ProjectForm
    model = Project

    def get_context_data(self, **kwargs):
        abtest_form = ABTestForm(prefix='abtest_form', instance=self.object.project_abtest)
        service_qs = Service.objects.all()
        if self.object.get_code_type == 'git':
            git_form = GitForm(prefix='git_form', instance=self.object.project_git)
            wget_form = WgetForm(prefix='wget_form')    # 编辑选择此选项时渲染
        else:
            wget_form = WgetForm(prefix='wget_form', instance=self.object.project_wget)
            git_form = GitForm(prefix='git_form')   # 编辑选择此选项时渲染
        kwargs.update(
            abtest_form=abtest_form,
            git_form=git_form,
            wget_form=wget_form,
            service_qs=service_qs
        )
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            operator = self.request.POST.getlist('operator[]')
            developer = self.request.POST.getlist('developer[]')
            kwargs['data'] = {}
            for k, v in self.request.POST.items():
                kwargs['data'].update({k: v})
            kwargs['data'].update(
                operator = operator,
                developer = developer,
                success = '更新成功',
                error = '更新失败'
            )
            kwargs['data'].pop('operator[]')
            kwargs['data'].pop('developer[]')
        return kwargs

    def form_valid(self, form):
        form_logs = []
        # 持久化ProjectForm表单
        form_ins = form.save()
        # 持久化GitForm、WgetForm表单
        if form.data['get_code_type'] == 'git':
            form.data['git_form-project'] = form_ins.id
            # 更新或创建
            git_form_ins = form_ins.project_git if hasattr(form_ins, 'project_git') else None
            git_form = GitForm(prefix='git_form', data=form.data, instance=git_form_ins)
            if git_form.is_valid():
                git_form.save()
            else:
                form_logs.append(git_form.errors.as_text())
        else:
            form.data['wget_form-project'] = form_ins.id
            # 更新或创建
            wget_form_ins = form_ins.project_wget if hasattr(form_ins, 'project_wget') else None
            wget_form = WgetForm(prefix='wget_form', data=form.data, instance=wget_form_ins)
            if wget_form.is_valid():
                wget_form.save()
            else:
                form_logs.append(wget_form.errors.as_text())
        # 处理ABTestForm表单
        service_hosts = form_ins.hosts.hosts.all()
        if form.data['abtest_form-mode'] == "0":
            abtest_hosts = []
            for host in service_hosts:
                if host.idc_id == int(form.data['abtest_form-idc']):
                    abtest_hosts.append(host.ip)
        elif form.data['abtest_form-mode'] == "1":
            percent = form.data['abtest_form-percent']
            abtest_hosts = []
            res = round(len(service_hosts) * int(percent) / 100)
            if res < 1:
                abtest_hosts.append(random.choice(service_hosts).ip)
            else:
                for n in range(res):
                    abtest_hosts.append(random.choice(service_hosts).ip)
        else:
            abtest_hosts = self.request.POST.get('abtest_form-hosts')
            if abtest_hosts:
                abtest_hosts = abtest_hosts.split(',')
            else:
                abtest_hosts = self.request.POST.getlist('abtest_form-hosts[]')
        form.data['abtest_form-hosts'] = ','.join(abtest_hosts)
        form.data['abtest_form-project'] = form_ins.id
        # 更新或创建
        abtest_form_ins = form_ins.project_abtest if hasattr(form_ins, 'project_abtest') else None
        abtest_form = ABTestForm(prefix='abtest_form', data=form.data, instance=abtest_form_ins)
        if abtest_form.is_valid():
            abtest_form.save()
        else:
            form_logs.append(abtest_form.errors.as_text())

        if not form_logs:
            return JsonResponse({
                'code': 0,
                'msg': form.data['success'],
                'results': form_ins.name
            })
        else:
            return JsonResponse({
                'code': 1,
                'msg': form.data['error'],
                'results': '\n'.join(form_logs)
            })

    def form_invalid(self, form):
        return JsonResponse({
            'code': 1,
            'msg': form.data['error'],
            'results': form.errors.as_text()
        })


class ProjectCopyView(ProjectUpdateView):
    """
    项目复制视图
    """

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            # 复制后项目name命名
            old_name = self.object.name
            new_name = kwargs['data']['name']
            if new_name == old_name:
                new_name = kwargs['data']['name'] + '_copy'
                kwargs['data']['name'] = new_name
            # 去除参数instance，执行form.save()创建新的实例
            kwargs.pop('instance', None)
            kwargs['data'].update(
                success='复制成功',
                error='复制失败'
            )
        return kwargs


class ProjectDeleteView(AccessDelete, DeleteBaseView):
    """
    项目删除视图
    """
    queryset = Project.objects.all()

