import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

from container.configs import *


class BlueOceanAPI(object):
    def __init__(self, host=jenkins_domain, user=jenkins_user, password=jenkins_pass):
        self.host = host
        self.user = user
        self.password = password
        self.auth = HTTPBasicAuth(self.user, self.password)
        self.base_url = f'http://{self.host}/blue/rest/organizations/jenkins/pipelines/%(job)s/runs/%(build_number)d/'

    def get_node_url(self, job, build_number):
        url = self.base_url % ({'job': job, 'build_number': build_number})
        node_url = urljoin(url, 'nodes/')
        return node_url

    def get_step_url(self, job, build_number, node_id):
        url = self.get_node_url(job, build_number)
        url_path = f'{node_id}/steps/'
        step_url = urljoin(url, url_path)
        return step_url

    def get_log_url(self, job, build_number, node_id, step_id):
        url = self.get_step_url(job, build_number, node_id)
        url_path = f'{step_id}/log/'
        log_url = urljoin(url, url_path)
        return log_url

    def get_nodes(self, job, build_number):
        node_list = []
        url = self.get_node_url(job, build_number)
        res = requests.get(url, auth=self.auth)
        if res.status_code != 200:
            return {
                'code': res.status_code,
                'msg': f'[{url}] 请求发生错误',
                'results': res.reason
            }
        else:
            results = res.json()
            for item in results:
                if item['type'] == 'STAGE':
                    node_list.append({
                        'node_id': int(item['id']),
                        'name': item['displayName'],
                        'state': item['state'],
                        'result': item['result']
                    })
            return {
                'code': 0,
                'msg': 'ok',
                'results': node_list
            }

    def get_steps(self, job, build_number):
        step_list = []
        nodes = self.get_nodes(job, build_number)
        if nodes['code'] != 0:
            return nodes
        else:
            for node in nodes['results']:
                url = self.get_step_url(job, build_number, node['node_id'])
                res = requests.get(url, auth=self.auth)
                if res.status_code != 200:
                    return {
                        'code': res.status_code,
                        'msg': f'[{url}] 请求发生错误',
                        'results': res.reason
                    }
                else:
                    results = res.json()
                    node['step'] = []
                    for item in results:
                        if item['type'] == "STEP":
                            node['step'].append({
                                'step_id': int(item['id']),
                                'name': item['displayName'],
                                'result': item['result'],
                                'state': item['state']
                            })
                    step_list.append(node)
            return {
                'code': 0,
                'msg': 'ok',
                'results': step_list
            }

    def get_step_logs(self, job, build_number):
        step_logs = []
        steps = self.get_steps(job, build_number)
        if steps['code'] != 0:
            return steps
        else:
            for item in steps['results']:
                node_id = item['node_id']
                for step in item['step']:
                    url = self.get_log_url(job, build_number, node_id, step['step_id'])
                    res = requests.get(url, auth=self.auth)
                    if res.status_code != 200:
                        return {
                            'code': res.status_code,
                            'msg': f'[{url}] 请求发生错误',
                            'results': res.reason
                        }
                    else:
                        log_content = res.text
                        step['log'] = log_content
                step_logs.append(item)
            return {
                'code': 0,
                'msg': 'ok',
                'results': step_logs
            }

    def get_all_logs(self, job, build_number):
        url = self.base_url % ({'job': job, 'build_number': build_number})
        all_logs_url = urljoin(url, 'log/')
        res = requests.get(all_logs_url, auth=self.auth)
        if res.status_code != 200:
            return {
                'code': res.status_code,
                'msg': f'[{all_logs_url}] 请求发生错误',
                'results': res.reason
            }
        else:
            all_logs = res.text
            return {
                'code': 0,
                'msg': 'ok',
                'results': all_logs
            }

blueoceanapi = BlueOceanAPI()


if __name__ == '__main__':
    from pprint import pprint
    import json
    job = 'go_admin'
    number = 418
    res = blueoceanapi.get_logs(job, number)
    print(json.dumps(res))
