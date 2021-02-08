from datetime import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from assets.models import Service, IDC
# Create your models here.

User = get_user_model()

FILE_MATCH = '\.py$|\.rb$|\.sh$|\.php$|\.java$|\.pl$|\.go$'

GET_CODE_TYPE = (
    ('git', 'Git'),
    ('wget', 'Wget')
)


class Project(models.Model):
    """
    业务模型
    """
    name = models.CharField(max_length=32, verbose_name="业务名称", unique=True)
    description = models.TextField(verbose_name="描述", blank=True, null=True)

    get_code_type = models.CharField(max_length=10, verbose_name="获取代码方式", choices=GET_CODE_TYPE, default='git')
    web_root = models.CharField(max_length=100, verbose_name="WebRoot")
    exclude_file = models.TextField(verbose_name="排除文件", blank=True, null=True)
    pre_script = models.FilePathField(verbose_name="前执行脚本", path=settings.FILE_PATH_FIELD_DIRECTORY,
                                      match=FILE_MATCH, recursive=True, blank=True, null=True)
    pre_script_args = models.CharField(max_length=100, verbose_name="前脚本参数", blank=True, null=True)
    post_script = models.FilePathField(verbose_name="后执行脚本", path=settings.FILE_PATH_FIELD_DIRECTORY,
                                       match=FILE_MATCH, recursive=True, blank=True, null=True)
    post_script_args = models.CharField(max_length=100, verbose_name="后脚本参数", blank=True, null=True)
    hosts = models.ForeignKey(Service, verbose_name="项目资产组", related_name="service_project", on_delete=models.SET_NULL, null=True)
    test_host = models.GenericIPAddressField(verbose_name='测试机器', blank=True, null=True)
    version_count = models.IntegerField(verbose_name="保留版本数量", choices=[(i, i) for i in range(0, 50)], default=20)

    operator = models.ManyToManyField(User, related_name="users_operators", verbose_name="运维", blank=True)
    developer = models.ManyToManyField(User, related_name="users_developers", verbose_name="开发", blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "业务/项目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{} || {}'.format(self.name, self.description)


AB_TEST_MODE = (
    (0, '按机房'),
    (1, '按占比'),
    (2, '按定量')
)
PERCENT_CHOICE = (
    (10, '10%'),
    (30, '30%'),
    (50, '50%'),
    (80, '80%'),
)


class ABTest(models.Model):
    """
    灰度方式
    """
    project = models.OneToOneField(Project, verbose_name="业务", related_name="project_abtest", on_delete=models.CASCADE)
    mode = models.SmallIntegerField(verbose_name="灰度方式", choices=AB_TEST_MODE, default=0)
    # 按机房
    idc = models.ForeignKey(IDC, verbose_name="按机房", related_name="idc_abtest", on_delete=models.SET_NULL, blank=True, null=True)
    # 按占比
    percent = models.SmallIntegerField(verbose_name='按比例', choices=PERCENT_CHOICE, blank=True, null=True)
    # 三种方式的机器；选择按机房、按比例(每次更新)后，将此项目资产组符合要求的机器添加到hosts字段
    hosts = models.CharField(max_length=1000, verbose_name="灰度机器", blank=True, null=True)

    class Meta:
        verbose_name = "灰度方式"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}项目{}方式发布".format(self.project.name,self.get_mode_display())


class Git(models.Model):
    """
    Git获取代码模型
    """
    project = models.OneToOneField(Project, verbose_name="所属业务", related_name='project_git', on_delete=models.CASCADE)
    git_pid = models.IntegerField(verbose_name="GitLab ID", null=True, blank=True)
    url = models.CharField(max_length=100, verbose_name="仓库代码地址")
    branch = models.CharField(max_length=32, verbose_name="线上环境分支名称", default='master')
    test_branch = models.CharField(max_length=32, verbose_name="测试环境分支名称", default='master')

    class Meta:
        verbose_name = "Git获取"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{} | {}'.format(self.url, self.branch)


class Wget(models.Model):
    """
    Wget获取代码模型
    """
    project = models.OneToOneField(Project, verbose_name="所属业务", related_name='project_wget', on_delete=models.CASCADE)
    url = models.CharField(max_length=100, verbose_name="下载地址")

    class Meta:
        verbose_name = "Wget获取"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.url


RECORD_STATUS = (
    (-1, '待介入'),    # 运维审核
    (0, '待审核'),     # 测试审核
    (1, '待发布'), # 已审核
    (2, '已灰度'),
    (3, '已发布'),
    (4, '作废')
)


class Record(models.Model):
    """
    发布记录模型
    """
    project = models.ForeignKey(Project, verbose_name="所属业务", related_name="project_record", on_delete=models.CASCADE)
    version = models.CharField(max_length=64, verbose_name="发布版本")
    notes = models.TextField(verbose_name="发布功能", blank=True, null=True)
    status = models.SmallIntegerField(verbose_name="记录状态", choices=RECORD_STATUS, default=0)
    approve_desc = models.TextField(verbose_name="审核说明", blank=True, null=True)
    if_operator = models.BooleanField(verbose_name="是否需要运维介入", default=False)
    what_operate = models.TextField(verbose_name="运维操作说明或内容", blank=True, null=True)
    released_hosts = models.CharField(max_length=1000, verbose_name="已发布的机器", blank=True, null=True)
    submitter = models.ForeignKey(User, verbose_name="提交者", related_name="user_submitter", on_delete=models.SET_NULL,
                                  null=True, blank=True)
    approver = models.ForeignKey(User, verbose_name="审核者", related_name="user_approver", on_delete=models.SET_NULL,
                                  null=True, blank=True)
    publisher = models.ForeignKey(User, verbose_name="发布者", related_name="user_publisher", on_delete=models.SET_NULL,
                                  null=True, blank=True)
    submit_time = models.DateTimeField(verbose_name="提交时间", auto_now_add=True)
    record_time = models.DateTimeField(verbose_name="事件时间", auto_now=True)

    class Meta:
        verbose_name = '发布记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} | {} | {}".format(self.project.name, self.version, self.submit_time)


class RecordLog(models.Model):
    record = models.OneToOneField(Record, verbose_name="发布记录", related_name='record_log', on_delete=models.CASCADE)
    logs = models.TextField(verbose_name='日志', blank=True, null=True)

    class Meta:
        verbose_name = '发布记录日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{} | {}".format(self.record.project.name, self.record.version)


class Permissions(models.Model):
    """发布系统开放日模型"""
    name = models.CharField(max_length=30, verbose_name="业务名称", unique=True)
    monday = models.BooleanField(verbose_name="星期一", default=True)
    tuesday = models.BooleanField(verbose_name="星期二", default=True)
    wednesday = models.BooleanField(verbose_name="星期三", default=True)
    thursday = models.BooleanField(verbose_name="星期四", default=True)
    friday = models.BooleanField(verbose_name="星期五", default=False)
    saturday = models.BooleanField(verbose_name="星期六", default=False)
    sunday = models.BooleanField(verbose_name="星期日", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "权限设置"
        verbose_name_plural = verbose_name


class FileUpload(models.Model):
    """
    脚本上传
    """
    script_file = models.FileField(upload_to="release_scripts", verbose_name="脚本文件")

    def __str__(self):
        return self.script_file.name

    class Meta:
        verbose_name = "脚本文件"
        verbose_name_plural = verbose_name