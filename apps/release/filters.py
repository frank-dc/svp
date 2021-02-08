import django_filters
from django.db.models import Q
from distutils.util import strtobool

from .models import *
from users.models import UsersProfile
from assets.models import Service


class M2MFilter(django_filters.Filter):

    def filter(self, qs, value):
        if not value:
            return qs
        values = value.split(',')
        for v in values:
            qs = qs.filter(status=v)
        return qs


class ProjectFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')
    get_code_type = django_filters.ChoiceFilter(choices=GET_CODE_TYPE)
    hosts = django_filters.ModelChoiceFilter(queryset=Service.objects.all())
    version_count = django_filters.NumberFilter(field_name='version_count', lookup_expr='icontains')
    create_time = django_filters.DateTimeFilter(field_name='create_time', lookup_expr='range')
    operator = django_filters.ModelMultipleChoiceFilter(queryset=UsersProfile.objects.all())    # 使用id查询
    # 使用username查询
    # operator = django_filters.ModelMultipleChoiceFilter(queryset=UsersProfile.objects.all(), field_name='operator__username', to_field_name='username')

    class Meta:
        model = Project
        fields = ['name', 'description', 'get_code_type', 'hosts', 'version_count', 'create_time']


class RecordFilter(django_filters.rest_framework.FilterSet):
    project = django_filters.CharFilter(field_name='project__name', lookup_expr='icontains')
    version = django_filters.CharFilter(field_name='version', lookup_expr='icontains')
    notes = django_filters.CharFilter(field_name='notes', lookup_expr='icontains')
    status = django_filters.MultipleChoiceFilter(choices=RECORD_STATUS)
    released_hosts = django_filters.CharFilter(field_name='released_hosts', lookup_expr='icontains')
    publisher = django_filters.ModelChoiceFilter(queryset=UsersProfile.objects.all())
    submitter = django_filters.ModelChoiceFilter(queryset=UsersProfile.objects.all())
    submit_time = django_filters.DateTimeFilter(field_name='submit_time', lookup_expr='date')
    record_time = django_filters.DateTimeFilter(field_name='record_time', lookup_expr='date')

    class Meta:
        model = Record
        fields = ['project', 'version', 'notes', 'status', 'released_hosts', 'publisher', 'submitter',
                  'submit_time']
