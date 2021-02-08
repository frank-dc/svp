import xadmin
from xadmin.filters import *

from .models import *


@xadmin.sites.register(Record)
class RecordAdmin(object):
    list_display = ('project', 'version', 'notes', 'status', 'submitter', 'approve_desc', 'approver',
                    'released_hosts', 'publisher', 'submit_time', 'record_time')
    list_display_links = ('project', )
    list_filter = ('project', 'version', 'notes', 'status', 'submitter', 'approve_desc', 'approver',
                    'released_hosts', 'publisher', 'submit_time', 'record_time')
    search_fields = ('project__name', 'version', 'notes', 'status', 'submitter__username', 'approve_desc', 'approver__username',
                    'released_hosts', 'publisher__username', 'submit_time', 'record_time')
    list_editable = ('project', 'version', 'notes', 'status', 'submitter', 'approve_desc', 'approver',
                    'released_hosts', 'publisher', 'submit_time', 'record_time')
    save_as = True
    model_icon = 'fa fa-location-arrow'


@xadmin.sites.register(Project)
class ProjectAdmin(object):
    list_display = ('name', 'description', 'get_code_type', 'web_root', 'exclude_file', 'pre_script',
                    'post_script', 'hosts', 'version_count', 'operator', 'developer')
    list_display_links = ('name', )
    list_filter = ('name', 'get_code_type', 'web_root', 'version_count', 'hosts',
                   ('operator', RelatedFieldSearchFilter),
                   ('developer', RelatedFieldSearchFilter))
    search_fields = ('name', 'get_code_type', 'web_root', 'version_count', 'hosts__name')
    list_editable = ('name', 'description', 'get_code_type', 'web_root', 'exclude_file', 'pre_script',
                    'post_script', 'hosts', 'version_count')
    save_as = True
    style_fields = {'operator': 'm2m_transfer', 'developer': 'm2m_transfer'}
    model_icon = 'fa fa-file-text'


@xadmin.sites.register(ABTest)
class ABTestAdmin(object):
    list_display = ('project', 'mode', 'hosts')
    list_display_links = ('project',)
    list_filter = ('project', 'mode', 'hosts')
    list_editable = ('mode', 'hosts')
    search_fields = ('project__name', 'mode', 'hosts')
    save_as = True
    model_icon = 'fa fa-delicious'


@xadmin.sites.register(Git)
class GitAdmin(object):
    list_display = ('project', 'url', 'branch')
    list_display_links = ('project', )
    list_filter = ('project__name', 'url', 'branch')
    search_fields = ('project__name', 'url', 'branch')
    list_editable = ('project', 'url', 'branch')
    save_as = True
    model_icon = 'fa fa-github'


@xadmin.sites.register(Wget)
class WgetAdmin(object):
    list_display = ('project', 'url')
    list_display_links = ('project', )
    list_filter = ('project__name', 'url')
    search_fields = ('project__name', 'url')
    list_editable = ('project', 'url')
    save_as = True
    model_icon = 'fa fa-file-zip-o'


@xadmin.sites.register(RecordLog)
class RecordLogAdmin(object):
    list_display = ('record', 'logs')
    list_display_links = ('record', )
    list_filter = ('record__version', )
    model_icon = 'fa fa-camera'
