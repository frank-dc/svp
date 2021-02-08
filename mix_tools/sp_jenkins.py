import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'small_platform.settings')
django.setup()
import re
import math
import time
import subprocess
import requests
import xmltodict
from collections import defaultdict
from requests.auth import HTTPBasicAuth
from jenkins import Jenkins
from collections import Iterable
from mix_tools.sp_subprocess import popen
from container.configs import jenkins_domain, jenkins_user, jenkins_pass
from container.configs import helm_host, helm_port
from commapi.models import GitlabProject
from mix_tools.sp_gitlab import cat_repository_file


def get_helm_history(name):
    """
    获取helm history revision
    :param name: helm name
    :return:
    """
    cmd = f"/usr/local/sbin/helm  --tls --tiller-namespace=kube-system --home=/data/helm/.helm --host={helm_host}:{helm_port} history {name}"
    ret = popen(cmd)
    assert ret['code'] == 0, '%(msg)s\n%(results)s' % ret
    res = subprocess.Popen("awk 'NR>1{print $1}'", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = res.communicate(input=ret['results'].encode())
    assert stderr is None, stderr.decode()
    results = stdout.decode().strip('\n').split('\n')
    return results


def commit_helm_builds(job):
    """git commit, helm id, jenkins builds对应关系"""


def init_jenkins():
    jenkins_url = f'http://{jenkins_domain}'
    username = jenkins_user
    password = jenkins_pass

    server = Jenkins(jenkins_url, username=username, password=password)
    return server


def get_jobs():
    server = init_jenkins()
    jobs = []
    ret = server.get_all_jobs()
    for item in ret:
        job_info = server.get_job_info(item['name'])
        last_build_info = job_info.get('lastBuild', None)
        last_build = last_build_info['number'] if last_build_info else None
        jobs.append({
            'name': item['name'],
            'url': item['url'],
            'last_build': last_build
        })
    return jobs


def get_job_builds(job):
    server = init_jenkins()
    builds = []
    ret = server.get_job_info(job)
    for item in ret['builds']:
        build_info = server.get_build_info(job, item['number'])
        builds.append({
            'number': item['number'],
            'url': item['url'],
            'duration': microseconds2human(build_info['duration']),
            'start_time': time2human(build_info['timestamp']),
            'status': build_info['result']
        })
    return sorted(builds, key=lambda k: k['number'])


def get_jenkinsfile(job):
    """获取jenkins任务的jenkinsfile名称"""
    server = init_jenkins()
    job_config_xml = server.get_job_config(job)
    job_config_dict = xmltodict.parse(job_config_xml)
    return job_config_dict['flow-definition']['definition']['scriptPath']


def get_gitlab_info(job):
    """获取jenkins任务gitlab地址，并得到gitlab项目ID"""
    server = init_jenkins()
    job_config_xml = server.get_job_config(job)
    job_config_dict = xmltodict.parse(job_config_xml)
    try:
        # 获取jenkins job配置的git地址
        git_url = job_config_dict['flow-definition']['definition']['scm']['userRemoteConfigs']['hudson.plugins.git.UserRemoteConfig']['url']
        print(git_url)
        if git_url.startswith('http'):
            git_path = '/'.join(git_url.split('/')[-2:])
        elif git_url.startswith('git'):
            git_path = git_url.split(':')[-1]
        else:
            git_path = "git地址不是http或ssh协议"
            return (1, git_path)
        namespace, name = git_path.split('/')
        name = name.split('.git')[0]
        # 从Model GitlabProject查询git id
        gp = GitlabProject.objects.get(name=name, namespace=namespace)
        git_id = gp.id
        return (0, git_path, git_id)
    except Exception as e:
        return (1, str(e))


def get_build_logs(job, number):
    try:
        server = init_jenkins()
        logs = server.get_build_console_output(job, number)
    except Exception as e:
        logs = (-1, str(e))
    return logs


def get_job_last_build_number(job):
    server = init_jenkins()
    job_info = server.get_job_info(job)
    try:
        last_build_number = job_info['lastBuild']['number']
    except Exception:
        last_build_number = 0
    return last_build_number


def execute_build(job, **kwargs):
    global build_number
    try:
        server = init_jenkins()
        build_ret = server.build_job(job, parameters=kwargs)
        queue_data = server.get_queue_item(build_ret)
        if queue_data.get('executable', None):
            build_number = queue_data.get('executable').get('number')
        else:
            flag = 0
            for n in range(100):
                flag += 1
                queue_data = server.get_queue_item(build_ret)
                if queue_data.get('executable', None):
                    build_number = queue_data.get('executable').get('number')
                    break
            if flag == 100:
                build_number = get_job_last_build_number(job) + 1
        return 0, build_number
    except Exception as e:
        return 1, str(e)

def microseconds2human(microseconds):
    assert isinstance(microseconds, int), '<%d> must be int type' % microseconds
    if microseconds < 1000:
        return f'{microseconds}ms'
    # second format
    seconds = microseconds / 1000
    if seconds < 60:
        return f'{round(seconds)}s'
    # minute format
    minute = seconds / 60
    if minute < 60:
        m_dot, m = math.modf(minute)
        return f'{int(m)}m {int(m_dot * 60)}s'
    # hour format
    hour = minute / 60
    h_dot, h = math.modf(hour)
    m_dot, m = math.modf(h_dot * 60)
    s = round(m_dot * 60)
    return f'{int(h)}h {int(m)}m {s}s'


def time2human(timestamp):
    assert isinstance(timestamp, int), '<%d> must be int type' % timestamp
    st = time.localtime(timestamp/1000)
    return time.strftime('%Y年%m月%d日 %H:%M:%S', st)


def jenkinsfile2json(jenkinsfile):
    if os.path.isfile(jenkinsfile):
        with open(jenkinsfile, 'r') as f:
            jenkinsfile_content = f.read()
    else:
        jenkinsfile_content = jenkinsfile
    url = f'http://{jenkins_domain}/pipeline-model-converter/toJson'
    username = jenkins_user
    password = jenkins_pass
    r = requests.post(url, data={'jenkinsfile': jenkinsfile_content}, auth=HTTPBasicAuth(username, password))
    if r.status_code == 200:
        response = r.json()
        if response['data']['result'].lower() == "success":
            json_data = response['data']['json']
            return {
                'code': 0,
                'msg': '解析成功',
                'results': json_data
            }
        else:
            return {
                'code': 1,
                'msg': '解析错误',
                'results': response['data']['errors'][0]['error']
            }
    else:
        return {
            'code': 1,
            'msg': '请求错误',
            'results': r.reason
        }


def extract_steps_from_jenkinsfile(job, gitlabid, action, branch="master"):
    """从jenkinsfile提取步骤"""
    step_list = []
    jenkinsfile_name = get_jenkinsfile(job)
    jenkinsfile_content = cat_repository_file(gitlabid, jenkinsfile_name, branch=branch)
    jenkinsfile_content_to_json = jenkinsfile2json(jenkinsfile_content)
    if jenkinsfile_content_to_json['code'] == 0:
        results = jenkinsfile_content_to_json['results']
        for item in results['pipeline']['stages']:
            this_action = item['when']['conditions'][0]['arguments'][1]['value']['value']
            if this_action == action:
                step_list.append((item['name'], 'execute'))
            else:
                step_list.append((item['name'], 'skip'))
        return 0, step_list
    else:
        return 1, jenkinsfile_content_to_json['results']


def analysis_jenkins_build_logs(iterable_obj, contents):
    """
    分析jenkins构建日志
    :param iterable_obj: ['Git代码拉取', '构建应用镜像', '线上发布', '版本回滚']
    :param contents: jenkins build console input
    :return:
    """
    def mid_handle_logs(logs):
        logs = re.sub('\[Pipeline\].*', '', logs)
        logs = re.sub('[\r\n\f]{2,}', '\n', logs).strip('\n')
        return logs

    def check_item_exist(step, contents):
        res = re.findall(step, contents)
        return bool(res)
    results = defaultdict(dict)
    assert isinstance(iterable_obj, Iterable), "%s must be Iterable" % iterable_obj
    for item in iterable_obj:
        item_if_exist = check_item_exist(item, contents)
        item_if_skipped = check_item_exist(f'Stage "{item}" skipped', contents)
        if item_if_exist:   # 步骤是否存在
            results[item]['exist'] = True
            if item_if_skipped:     # 步骤是否执行
                results[item].update(status='skip', done=False)
            else:
                results[item]['status'] = 'execute'
                if iterable_obj.index(item) == 0:   # item 为第一个元素
                    item_1_if_exist = check_item_exist(iterable_obj[1], contents)
                    if item_1_if_exist:
                        mid_logs = re.findall(f'(.*){iterable_obj[1]}\)', contents, re.S)[0]
                        mid_logs = mid_handle_logs(mid_logs)
                        results[item]['done'] = True
                    else:
                        mid_logs = mid_handle_logs(contents)
                        results[item]['done'] = False
                    results[item]['logs'] = mid_logs
                elif iterable_obj.index(item) == len(iterable_obj) - 1:     # item 为最后一个元素
                    mid_logs = re.findall(f'{item}\)(.*)', contents, re.S)[0]
                    results[item]['done'] = True if re.findall('Finished:.*', mid_logs) else False
                    mid_logs = mid_handle_logs(mid_logs)
                    results[item]['logs'] = mid_logs
                else:       # item 为中间元素
                    next_index = iterable_obj.index(item) + 1
                    next_item = iterable_obj[next_index]
                    item_next_if_exist = check_item_exist(next_item, contents)
                    if item_next_if_exist:
                        mid_logs = re.findall(f'{item}\)(.*){next_item}\)', contents, re.S)[0]
                        results[item]['done'] = True
                    else:
                        mid_logs = re.findall(f'{item}\)(.*)', contents, re.S)[0]
                        results[item]['done'] = False
                    mid_logs = mid_handle_logs(mid_logs)
                    results[item]['logs'] = mid_logs
        else:
            results[item].update(exist=False, done=False)
    return results



if __name__ == '__main__':
    # data = {'Action': 'roll-update', 'branch': 'master', 'CommitID': '308f5d581508fc562767cbde09e99bded614640a'}
    # build_ret = execute_build('go_admin', **data)
    # print(build_ret)
    name = "pub-athena-auth"
    res = get_gitlab_info(name)
    print(res)
