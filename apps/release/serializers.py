from rest_framework import serializers

from .models import *
from assets.serializers import ServiceSerializer


class GitSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='name', queryset=Project.objects.all())

    class Meta:
        model = Git
        fields = '__all__'


class WgetSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='name', queryset=Project.objects.all())

    class Meta:
        model = Wget
        fields = '__all__'

class ABTestSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='name', queryset=Project.objects.all())
    mode = serializers.CharField(source='get_mode_display')

    class Meta:
        model = ABTest
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    get_code_type = serializers.CharField(source='get_get_code_type_display')
    hosts = ServiceSerializer()
    operator = serializers.SlugRelatedField(slug_field='full_name', many=True, queryset=User.objects.all())
    developer = serializers.SlugRelatedField(slug_field='full_name', many=True, queryset=User.objects.all())
    create_time = serializers.DateTimeField(format="%Y年%m月%d日 %H:%M:%S")
    project_abtest = ABTestSerializer()
    project_wget = WgetSerializer()
    project_git = GitSerializer()

    class Meta:
        model = Project
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    project = serializers.SlugRelatedField(slug_field='name', queryset=Project.objects.all())
    publisher = serializers.SlugRelatedField(slug_field='full_name', queryset=User.objects.all())
    approver = serializers.SlugRelatedField(slug_field='full_name', queryset=User.objects.all())
    submitter = serializers.SlugRelatedField(slug_field='full_name', queryset=User.objects.all())
    submit_time = serializers.DateTimeField(format="%Y年%m月%d日 %H:%M:%S")
    record_time = serializers.DateTimeField(format="%Y年%m月%d日 %H:%M:%S")

    class Meta:
        model = Record
        fields = '__all__'
