from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger('release')

@shared_task
def async_sendmail(subject, message, recipient_list, from_email='svp.mobileztgame.com', **kwargs):
    try:
        recipient_list.append('dengchao@ztgame.com')
        recipient_list = sorted(list(set(recipient_list)))
        html_msg = kwargs.get('html_msg', None)
        send_mail(subject, message, from_email, recipient_list, html_message=html_msg)
        return {"code": 0, "msg": "发送成功", 'results': message}
    except Exception as e:
        return {"code": 1, "msg": '发送异常', 'results': str(e)}
