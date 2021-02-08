from django.urls import path

from .views import *

app_name = 'release'

urlpatterns = [
    path('project/list/', ProjectListView.as_view(), name='project_list'),
    path('project/create/', ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/copy/', ProjectCopyView.as_view(), name='project_copy'),
    path('project/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    path('record/create/', RecordCreateView.as_view(), name='record_create'),
    path('record/<int:pk>/intervene/', OperatorInterventionView.as_view(), name='operator_intervene'),
    path('approve/list/', ApproveListView.as_view(), name='approve_list'),
    path('approve/<int:pk>/update/', ApproveUpdateView.as_view(), name='approve_update'),
    path('approve/delete/', ApproveDeleteView.as_view(), name='approve_delete'),
    path('record/list/', RecordListView.as_view(), name='record_list'),
    path('record/<int:pk>/detail/', RecordDetailView.as_view(), name='record_detail'),
    path('record/delete/', RecordDeleteView.as_view(), name='record_delete'),
    path('record/discard/', RecordDiscardView.as_view(), name='record_discard'),
    path('record/<int:pk>/log/', RecordLogView.as_view(), name='record_log'),
    path('execute/<int:pk>/release/', ExecuteReleaseView.as_view(), name='execute_release'),
    path('abtest/confirm/', ABTestConfirmView.as_view(),name='abtest_confirm'),
    path('test/release/', TestReleaseView.as_view(), name='test_release'),

    path('retrieve/commits/', RetrieveGitCommits.as_view(), name='retrieve_commits'),
    path('retrieve/branches/', RetrieveProjectBranch.as_view(), name='retrieve_branches'),
    path('setpermissions/<str:system>/', PermissionsSetView.as_view(), name='set_permissions'),
    path('fileupload/', FileUploadView.as_view(), name='file_upload'),
]
