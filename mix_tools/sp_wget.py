from urllib import request
import zipfile
import os

from mix_tools.sp_gitpython import web_dir

def wget(project, url, content_type='zip'):
    filename = '{}/{}.{}'.format(web_dir, project, content_type)
    try:
        wget_ret = request.urlretrieve(url, filename)
        if content_type == 'zip':
            try:
                zp = zipfile.ZipFile(filename, mode='r')
                zp.extractall(path=web_dir, members=zp.namelist())
                os.remove(filename)
            except Exception as e:
                return {
                    'code': 1,
                    'msg': '解压文件异常！',
                    'results': str(e)
                }
        else:
            return {
                'code': 1,
                'msg': '目前只提供zip类型解压',
                'results': '目前只提供zip类型解压'
            }
        return {
            'code': 0,
            'msg': '文件下载并解压完成',
            'results': wget_ret[0]
        }
    except Exception as e:
        return {
            'code': 1,
            'msg': '下载异常！',
            'results': str(e)
        }


if __name__ == '__main__':
    res = wget('payment3', 'http://cmdb.mobileztgame.com/dd/payment3.zip')
    print(res)