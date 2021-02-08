import subprocess
import shlex
import re


def rsync(host, web_root, project_code_dir, exclude):
    """
    代码分发
    :return:
    """
    cmd_rsync = 'rsync -avz --timeout=5 --exclude=%s %s %s:%s' % (
        exclude, project_code_dir, host, web_root
    )
    popen_ret = popen(cmd_rsync)
    popen_ret.update(host=host)
    return popen_ret


def popen(args):
    """
    封装subprocess.Popen，本地执行脚本或者命令
    :return:
    """
    assert isinstance(args, str), 'args must be a string!'
    try:
        # popen_ret = subprocess.Popen(shlex.split(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        popen_ret = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = popen_ret.communicate()
        if stderr:
            return {
                'code': 1,
                'msg': '# 执行[%s]有错误输出！' % args,
                'results': stderr.decode()
            }
        else:
            stdout = stdout.decode()
            return {
                'code': 0,
                'msg': '# 执行[%s]成功' % args,
                'results': stdout
            }
    except Exception as e:
        return {
            'code': 1,
            'msg': '# 执行[%s]异常！' % args,
            'results': str(e)
        }

if __name__ == '__main__':
    # res = popen('rsync -avz --timeout=3 --exclude={.git,.gitignore,.svn} /data/.virtualenvs/small_platform/WebDir/test/ 10.20.49.217:/home/ptweb/test')
    res = popen("curl -v 'https://passport-api.sdk.mobileztgame.com' --resolve 'passport-api.sdk.mobileztgame.com:443:101.132.224.10'")
    print(res)
