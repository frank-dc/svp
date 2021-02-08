import datetime

from django.shortcuts import render
from django.http import JsonResponse
from django.forms.models import model_to_dict
from release.models import Permissions
from enum import Enum

"""
权限类命名方式
已Access开头，加上类名 || 动作 || 角色+动作
"""


class BasePermRequiredMixin(object):
    role_list = []
    my_template = None
    return_type = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.get_role_display() not in self.role_list:
            if self.return_type == 'template':
                return render(request, self.my_template, {'role_list': self.role_list})
            else:
                return JsonResponse({
                    'code': 1,
                    'msg': '您在干嘛？',
                    'results': '不要调皮，您没有权限！'
                })
        return super().dispatch(request, *args, **kwargs)

# Access + 类名

class AccessRecordCreate(BasePermRequiredMixin):
    """
    周五及周末只有mabo有权限
    其它时间只有【开发、管理员】有权限
    """
    role_list = ['开发', '管理员']
    my_template = 'forbidden_release.html'
    return_type = 'template'

    def get_forbid_week(self):
        week_list = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
        Week = Enum('Week', week_list)

        try:
            p = Permissions.objects.get(name='release')
            p_data = model_to_dict(p)
            forbid_week = [getattr(Week, week).value for week in week_list if not p_data.get(week)]
        except Exception:
            forbid_week = [5, 6, 7]
        return forbid_week

    def dispatch(self, request, *args, **kwargs):
        if request.user.username in ['mabo', 'admin']:
            return super().dispatch(request, *args, **kwargs)
        else:
            today_week = datetime.datetime.now().isoweekday()
            if today_week in self.get_forbid_week():
                return render(request, self.my_template, {'role_list': self.role_list})
            return super().dispatch(request, *args, **kwargs)


class AccessExecuteRelease(AccessRecordCreate):
    """
    对<执行发布>拥有权限的角色
    """
    role_list = ['测试', '产品', '运维', '管理员']

# Access + 角色

class AccessOperator(BasePermRequiredMixin):
    """
    允许【运维、管理员】操作
    """
    role_list = ['运维', '管理员']
    my_template = '403.html'
    return_type = 'template'


class AccessDeveloper(BasePermRequiredMixin):
    """
    允许【开发、管理员】操作
    """
    role_list = ['开发', '管理员']
    my_template = '403.html'
    return_type = 'template'


class AccessTester(BasePermRequiredMixin):
    """
    允许【测试、管理员】操作
    """
    role_list = ['测试', '管理员']
    my_template = '403.html'
    return_type = 'template'


# Access + 角色 + 动作

class AccessDeveloperDelete(BasePermRequiredMixin):
    role_list = ['开发', '运维', '管理员']
    return_type = 'json'


class AccessTesterDelete(BasePermRequiredMixin):
    role_list = ['测试', '运维', '管理员']
    return_type = 'json'

# Access + 动作

class AccessDelete(BasePermRequiredMixin):
    role_list = ['运维', '管理员']
    return_type = 'json'


# old
class AdminPermRequiredMixin(object):
    """Verify that the current user is granted to operator."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.get_role_display() not in ['运维', '管理员']:
            return render(request, '403.html', locals())
        return super().dispatch(request, *args, **kwargs)


class TestPermRequiredMixin(object):
    """Verify that the current user is granted to test."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.get_role_display() not in ['测试', '产品', '管理员']:
            return render(request, '403.html', locals())
        return super().dispatch(request, *args, **kwargs)


class DeveloperPermRequiredMixin(object):
    """Verify that the current user is granted to developer."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.get_role_display() not in ['开发', '运维', '管理员']:
            return render(request, '403.html', locals())
        return super().dispatch(request, *args, **kwargs)


class DeletePermRequiredMixin(object):
    """Verify that the current user has delete permission."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.get_role_display() not in ['开发', '运维', '管理员']:
            return JsonResponse({
                'code': 1,
                'msg': '您在干嘛？',
                'results': '不要调皮，您没有权限！'
            })
        return super().dispatch(request, *args, **kwargs)


class DeleteAdminPermRequiredMixin(object):
    """Only administrator and operator are granted to delete permission"""
    def dispatch(self, request, *args, **kwargs):
        if request.user.get_role_display() not in ['运维', '管理员']:
            return JsonResponse({
                'code': 1,
                'msg': '您在干嘛？',
                'results': '不要调皮，您没有权限！'
            })
        return super().dispatch(request, *args, **kwargs)