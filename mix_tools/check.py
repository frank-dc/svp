import re

def check_ipv4_is_valid(ip):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False


def check_script_type(script_path):
    if re.search('.py$', script_path, flags=re.I):
        interpreter = '/data/.virtualenvs/python3.6.8/bin/python3'
        return {'code': 0, 'interpreter': interpreter}
    elif re.search('.sh$', script_path, flags=re.I):
        interpreter = 'bash'
        return {'code': 0, 'interpreter': interpreter}
    elif re.search('.php$', script_path, flags=re.I):
        interpreter = 'php'
        return {'code': 0, 'interpreter': interpreter}
    else:
        interpreter = '未知脚本类型'
        return {'code': 1, 'interpreter': interpreter}