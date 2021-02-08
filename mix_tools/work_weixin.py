import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'small_platform.settings')
django.setup()

import requests
import datetime
from urllib.parse import urljoin

from tool.models import WXAppToken
from db_tools.sp_redis import rediscli
from mix_tools import send_sms

corpid = ''
agentid = ''
secret = corpsecret = ''
mobile = 'xxx'  # 请求异常另外发短信通知

WX_URL = 'https://qyapi.weixin.qq.com'


def get_token(id=corpid, secret=corpsecret):
    """
    获取token
    :param id:
    :param secret:
    :return:
    """
    token = rediscli.conn.get('svp_wx_token')
    if token:
        return token
    else:
        for n in range(5):  # 有可能获取不到
            url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (id, secret)
            r = requests.get(url)
            results = r.json()
            if 'access_token' in results:
                token = results['access_token']
                rediscli.conn.set('svp_wx_token', token, results['expires_in'])
                return token
            else:
                continue


def upload_image(filename):
    """
    上传临时素材
    :param filename:
    :return:
    """
    token_ret = get_token()
    if token_ret['errcode'] == 0 and 'access_token' in token_ret:
        url = 'https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image' % token_ret.get('access_token')
        headers = {'Content-Type': 'multipart/form-data'}
        files = {
            'file': (filename, open(filename, 'rb'), 'application/octet-stream'),
        }
        r = requests.post(url, headers=headers, files=files)
        return r.json()


def send_msg(touser=None, toparty=None, content_type=None, content=None, media_id=None, tourl=None):
    """
    发送消息
    :param touser: 消息接收者，多个接收者用'|'分隔，最多支持1000个
    :param content: 消息内容，最长不超过2048个字节，超过将截断（支持id转译）
    :return:
    """
    token = get_token()
    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s' % token
    data = {
        'touser': touser,
        'toparty': toparty,
        'msgtype': content_type,
        'agentid': agentid,
        'safe': 0
    }
    if content_type == 'text':
        data.update(text={'content': content})
    elif content_type == 'image':
        data.update(image={'media_id': media_id})
    elif content_type == 'textcard':
        data.update(textcard={
            'title': '灰度超时通知',
            'description': '<div class="gray">%s</div> <div class="normal">已灰度发布单时间超过两小时</div><div class="highlight">请相关人员核实并执行全量发布</div>' % datetime.datetime.now().strftime('%Y年%m月%d日%H时'),
            'url': tourl,
            'btntxt': '查看详情'
        })
    else:
        return {
            'code': 1,
            'msg': '参数错误！',
            'result': 'Argument `content_type` is must be provided!'
        }
    header = {'Content-Type': 'application/json'}
    print(data)
    r = requests.post(url, json=data, headers=header)
    response = r.json()
    if response['errcode'] == 0:
        return {
            'code': 0,
            'msg': '发送成功',
            'results': ''
        }
    else:
        return {
            'code': 1,
            'msg': '发送失败',
            'results': response['errmsg']
        }


class SendWXMSGMixin(object):
    queryset = WXAppToken.objects.all()

    def __init__(self, app=None):
        self.app = app

    def get_object(self):
        queryset = self.queryset.filter(app=self.app)
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Exception("No %s found matching the query" % queryset.model._meta.object_name)
        return obj

    def get_token(self):
        token = rediscli.conn.get(f'{self.app}_wx_token')
        if token:
            return {
                'code': 0,
                'msg': 'ok',
                'results': token
            }
        else:
            object = self.get_object()
            params = {'corpid': corpid, 'corpsecret': object.secret}
            endpoint = '/cgi-bin/gettoken'
            this_url = urljoin(WX_URL, endpoint)
            for n in range(10):
                r = requests.get(this_url, params=params)
                if r.status_code == 200 and r.json()['errcode'] == 0 and 'access_token' in r.json():
                    results = r.json()
                    token = results['access_token']
                    rediscli.conn.set(f'{self.app}_wx_token', token, results['expires_in'])
                    return {
                        'code': 0,
                        'msg': 'ok',
                        'results': token
                    }
                elif n == 9:
                    if r.status_code == 200:
                        send_sms(mobile, f'【获取token】返回有错误，{r.json()["errmsg"]}')
                        return {
                            'code': 1,
                            'msg': '返回错误',
                            'results': r.json()['errmsg']
                        }
                    else:
                        send_sms(mobile, f'【获取token】请求接口错误，{r.status_code}')
                        return {
                            'code': 1,
                            'msg': '请求错误',
                            'results': r.status_code
                        }
                else:
                    continue

    def get_url_body(self):
        ret = self.get_token()
        if ret['code'] == 0:
            token = ret['results']
            endpoint = f'/cgi-bin/message/send?access_token={token}'
            this_url = urljoin(WX_URL, endpoint)
            body = {
                'touser': self.touser,
                'toparty': self.toparty,
                'msgtype': self.send_type,
                'agentid': self.get_object().agentid,
                'safe': 0
            }
            return 0, this_url, body
        else:
            return ret['code'], ret['msg'], ret['results']


class CommonSendWXMSG(SendWXMSGMixin):
    """通用接口"""

    def __init__(self, touser=None, toparty=None, content=None, send_type=None, **kwargs):
        self.touser = touser
        self.toparty = toparty
        self.content = content
        self.send_type = send_type
        super().__init__(app=kwargs.get('app', None))

    def send(self, url, body):
        header = {'Content-Type': 'application/json'}
        r = requests.post(url, json=body, headers=header)
        if r.status_code == 200 and r.json()['errcode'] == 0:
            return {
                'code': 0,
                'msg': '发送成功',
                'results': ''
            }
        else:
            error = f'请求接口错误，{r.status_code}' if r.status_code != 200 else f"返回有错误，{r.json()['errmsg']}"
            send_sms(mobile, f'【发送消息】有异常，{error}')
            return {
                'code': 1,
                'msg': '发送失败',
                'results': r.json()['errmsg']
            }

    def send_text(self):
        status, msg, results = self.get_url_body()
        if status != 0:
            return {
                'code': 1,
                'msg': msg,
                'results': results
            }
        else:
            url, body = msg, results
            body.update(
                text={'content': self.content}
            )
            res = self.send(url, body)
            return res

    def send_image(self):
        status, msg, results = self.get_url_body()
        if status != 0:
            return {
                'code': 1,
                'msg': msg,
                'results': results
            }
        else:
            url, body = msg, results
            body.update(
                image={'media_id': self.content}
            )
            res = self.send(url, body)
            return res

    def __call__(self, *args, **kwargs):
        if self.send_type == 'text':
            return self.send_text()
        elif self.send_type == 'image':
            return self.send_image()
        else:
            return {
                'code': 1,
                'msg': '参数错误！',
                'result': 'Argument `send_type` is must be provided!'
            }

if __name__ == '__main__':
    ins = CommonSendWXMSG(touser='dengchao', content="这是一条测试消息", send_type='text', app='svp')
    results = ins()
    print(results)
