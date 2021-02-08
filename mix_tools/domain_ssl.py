import re
import datetime
from dns import resolver
from .sp_subprocess import popen

nameservers = ['202.96.209.5', '202.96.209.133', '180.76.76.76']

def get_domain_resolvers(domain):
    results = []
    r = resolver.Resolver()
    r.nameservers = nameservers
    res = r.query(domain, 'A')
    for item in res:
        results.append(item.address)
    return results


def get_ssl_expiration(domain):
    domain_nameserver = get_domain_resolvers(domain)[0]
    cmd = f'curl -sv https://{domain} --connect-timeout 10 --resolve "{domain}:443:{domain_nameserver}"'
    try:
        popen_ret = popen(cmd)
        if '异常' in popen_ret['msg']:
            return popen_ret
        else:
            result = popen_ret['results']
            re_expire_date = re.search('expire date: .*', result, re.I)
            re_start_date = re.search('start date: .*', result, re.I)
            if re_expire_date and re_start_date:
                expire_date_str = re_expire_date.group().split(": ")[1]
                start_date_str = re_start_date.group().split(": ")[1]
                expire_date = datetime.datetime.strptime(expire_date_str, '%b %d %H:%M:%S %Y %Z')
                start_date = datetime.datetime.strptime(start_date_str, '%b %d %H:%M:%S %Y %Z')
                remain_days = (expire_date - datetime.datetime.now()).days
                return {
                    "code": 0,
                    'msg': '',
                    'results': {
                        'notbefore': start_date,
                        'notafter': expire_date,
                        'remain_days': remain_days
                    }
                }
            else:
                return {
                    'code': 1,
                    'msg': '未取到数据',
                    'results': ''
                }
    except Exception as e:
        return {
            'code': 1,
            'msg': '发生错误',
            'results': str(e)
        }


if __name__ == '__main__':
    domain = 'stat.sdk.mobileztgame.com'
    res = get_ssl_expiration(domain)
    print(res)
