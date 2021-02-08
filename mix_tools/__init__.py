#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
Name: __init__.py
Author: dengchao
Time: 2019/7/30 15:16
Illustration: 
"""
import requests

def send_sms(mobile, content, priority=5, gametype=2, acttype=66):
    """
    发送短信
    mobile: 手机号，不支持群发短信
    content：短信内容（GB2312编码），长度不能大于256个字节
    priority：短信优先级，1-5个级别。1最低，5最高
    其它参数参考"http://ptdoc.ztgame.com/pc_service/wiki/"
    """
    url = 'http://smcdserver.ztgame.com:29997/emaysendMsg'

    params = {}
    params.update({
        'dest_mobile': mobile,
        'msg_content': content.encode('gbk'),
        'priority': priority,
        'gametype': gametype,
        'acttype': acttype
    })
    try:
        requests.get(url, params=params)
        return 0
    except Exception:
        return 0


if __name__ == '__main__':
    send_sms('17621938005', 'hello world')