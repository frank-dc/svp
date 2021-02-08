from django import forms

from .models import (Project, ABTest, Git, Wget, Record,
                     Permissions, FileUpload)
from .models import FILE_MATCH
from django.conf import settings


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pre_script'].__init__(path=settings.FILE_PATH_FIELD_DIRECTORY, match=FILE_MATCH, recursive=True,
                                           required=False, label="前脚本")
        self.fields['post_script'].__init__(path=settings.FILE_PATH_FIELD_DIRECTORY, match=FILE_MATCH, recursive=True,
                                            required=False, label="后脚本")


class ABTestForm(forms.ModelForm):
    class Meta:
        model = ABTest
        fields = '__all__'


class GitForm(forms.ModelForm):
    class Meta:
        model = Git
        fields = '__all__'


class WgetForm(forms.ModelForm):
    class Meta:
        model = Wget
        fields = '__all__'


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = '__all__'


class PermissionsForm(forms.ModelForm):
    class Meta:
        model = Permissions
        fields = '__all__'


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = '__all__'