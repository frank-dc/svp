from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from custom.rest_framework.views import CustomModelViewset
from custom.rest_framework.pageination import CustomPagination
from .serializers import *
from .models import *
from .filters import *


class ProjectViewset(CustomModelViewset):
    """
    项目管理视图集
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ProjectFilter
    search_fields = ('name', 'description', 'get_code_type', 'web_root', 'exclude_file', 'pre_script',
                     'post_script', 'hosts__name', 'version_count')
    ordering_fields = ('name', 'get_code_type', 'hosts__name', 'version_count')
    ordering = ('name', )
    lookup_field = 'name'


class RecordViewset(CustomModelViewset):
    """
    发布记录视图集
    """
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = RecordFilter
    search_fields = ('project__name', 'version', 'if_approve', 'released_hosts', 'publisher__full_name',
                     'submitter__full_name', 'submit_time', 'record_time')
    ordering_fields = ('project__name', 'version', 'if_approve', 'released_hosts', 'publisher__full_name',
                     'submitter__full_name', 'submit_time', 'record_time')
    ordering = ('-record_time', )


class GitViewset(CustomModelViewset):
    """
    git获取代码视图集
    """
    queryset = Git.objects.all()
    serializer_class = GitSerializer
    pagination_class = CustomPagination


class WgetViewset(CustomModelViewset):
    """
    wget获取代码视图集
    """
    queryset = Wget.objects.all()
    serializer_class = WgetSerializer
    pagination_class = CustomPagination
