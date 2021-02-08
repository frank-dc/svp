#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
Name: sp_email
Author: dengchao
Time: 2019/12/10 14:18
Illustration:
"""
from release.tasks import async_sendmail
from django.template import loader
from functools import partial


def send_email_for_release(subject, *, recipient_list=['dengchao@ztgame.com', ], **kwargs):
    """
    发布系统发送邮件
    :param subject: 邮件主题
    :param recipient_list:  收件人
    :param kwargs: kwargs is a dict, include follow keys:
            'project': '发布项目',
            'version': '版本号',
            'notes': '发布功能',
            'submitter': '提交者',
            'submit_time': '提交时间',
            'approve_desc': '审核说明',
            'approver': '审核者',
            'publisher': '发布者',
            'record_time': '发布时间',
            'released_hosts': '发布机器'
    :return:
    """
    mail_msg_dict = dict()
    html_msg_dict = dict()
    keys = {
        'project': '发布项目',
        'version': '版本号',
        'notes': '发布功能',
        'submitter': '提交者',
        'if_operator': '需要运维介入',
        'what_operate': '运维操作说明或内容',
        'submit_time': '提交时间',
        'approve_status': '审核状态',
        'approve_desc': '审核说明',
        'approver': '审核者',
        'publisher': '发布者',
        'record_time': '发布时间',
        'released_hosts': '发布机器'
    }
    for k,v in keys.items():
        if kwargs.get(k, None):
            mail_msg_dict.update({v: kwargs.get(k)})
            html_msg_dict.update({k: kwargs.get(k)})
    mail_msg = ''
    for k,v in mail_msg_dict.items():
        mail_msg += '%s: %s\n' % (k, v)
    mail_msg = mail_msg.strip()
    html_msg = loader.render_to_string('email/release_notice.html', html_msg_dict)
    try:
        async_result = async_sendmail.delay(subject, mail_msg, recipient_list, html_msg=html_msg)
        return {'code': 0, 'msg': '发送邮件成功', 'results': mail_msg, 'async_result': async_result}
    except Exception as e:
        return {'code': 1, 'msg': '发送邮件失败', 'results': str(e)}


def base_send_email(subject, recipient_list, send_keys={}, **kwargs):
    """
    基础发送邮件函数，根据不同业务提供send_keys调用偏函数生成特定业务邮件发送函数
    :param subject:
    :param recipient_list:
    :param send_keys:
    :param kwargs:
    :return:
    """
    mail_msg_dict = dict()
    html_msg_dict = dict()
    assert bool(send_keys), f"{send_keys} cannot be a null dict"
    for k,v in send_keys.items():
        if kwargs.get(k, None):
            mail_msg_dict.update({v: kwargs.get(k)})
            html_msg_dict.update({k: kwargs.get(k)})
    mail_msg = []
    for k, v in mail_msg_dict.items():
        mail_msg.append(f'{k}: {v}')
    mail_msg = '\n'.join(mail_msg)
    html_msg = loader.render_to_string('email/base_email.html', locals())
    try:
        async_result = async_sendmail.delay(subject, mail_msg, recipient_list, html_msg=html_msg)
        return {'code': 0, 'msg': '发送邮件成功', 'results': mail_msg, 'async_result': async_result}
    except Exception as e:
        return {'code': 1, 'msg': '发送邮件失败', 'results': str(e)}

send_keys_of_create_record = {
    'job': '任务',
    'helm': 'Helm 名称',
    'branch': '分支/标签',
    'version': 'Git版本号',
    'submitter': '提交人员',
    'submit_time': '提交时间'
}

send_keys_of_jenkins_release = {
    'job': '任务',
    'branch': '分支|标签',
    'version': '版本号',
    'status': '当前状态',
    'publisher': '发布人员',
    'publish_time': '发布时间',
    'count_rollback_c': '容器环境回滚次数',
    'count_rollback_p': '物理环境回滚次数',
    'result': '发布结果'
}

send_keys_of_container_update = {
    'release_action': '发布动作',
    'job': '任务',
    'helm': 'Helm 名称',
    'branch': '分支/标签',
    'version': 'Git版本号',
    'publisher': '发布者',
    'publish_time': '发布完成时间'
}
send_keys_of_container_rollback = {
    'release_action': '发布动作',
    'job': '任务',
    'helm': 'Helm 名称',
    'version': 'Helm 版本号',
    'publisher': '发布者',
    'publish_time': '发布完成时间'
}
send_email_for_container_record_create = partial(base_send_email, send_keys=send_keys_of_create_record)
send_email_for_jenkins_release = partial(base_send_email, send_keys=send_keys_of_jenkins_release)

send_email_for_container_update = partial(base_send_email, send_keys=send_keys_of_container_update)
send_email_for_container_rollback = partial(base_send_email, send_keys=send_keys_of_container_rollback)


if __name__ == '__main__':
    import os, django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'small_platform.settings')
    django.setup()
    res = send_email_for_container_update('测试主题', recipient_list=['dengchao@ztgame.com'], job='go_admin', helm='go-admin-ui',
                             version='fb3409647bef2bd27b190aaab6e86dcfb5c05d84', product='测试发布', publisher='邓超',
                             publish_time='2020年4月29日 13:07')
    print(res)