import json
import shutil
import os

import ansible.constants as C
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.module_utils.common.collections import ImmutableDict
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible import context


def check_file_exists(fp, new_dir='/'):
    """
    检测文件路径是否存在，不存在则在new_dir下查找
    """
    if not os.path.exists(fp):
        new_fp = os.path.join(new_dir, os.path.basename(fp))
        if not os.path.exists(new_fp):
            return 1, f"{fp}、{new_fp}不存在"
        else:
            return 0, new_fp
    else:
        return 0, fp


class JSONCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_ok = []
        self.host_unreachable = []
        self.host_failed = []
        self.host_skipped = []

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable.append({host.get_name(): result})

    def v2_runner_on_ok(self, result):
        host = result._host
        self.host_ok.append({host.get_name(): result})

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host
        self.host_failed.append({host.get_name(): result})

    def v2_runner_on_skipped(self, result):
        host = result._host
        self.host_skipped.append({host.get_name(): result})

    def print_stdout(self):
        print(" UP ".center(90, '*'))
        for item in self.host_ok:
            for host, result in item.items():
                print('{0} >>> {1}'.format(host, result._result))

        print(" FAILED ".center(90, '*'))
        for item in self.host_failed:
            for host, result in item.items():
                print('{0} >>> {1}'.format(host, result._result))

        print(" UNREACHABLE ".center(90, '*'))
        for item in self.host_unreachable:
            for host, result in item.items():
                print('{0} >>> {1}'.format(host, result._result))

        print(" SKIPPED ".center(90, '*'))
        for item in self.host_skipped:
            for host, result in item.items():
                print('{0} >>> {1}'.format(host, result._result))


def playbook(playbooks, sources, **kwargs):
    context.CLIARGS = ImmutableDict(
        connection='smart',
        ask_pass=kwargs.get('ask_pass', False),
        private_key_file=kwargs.get('private_key_file', None),
        remote_user=kwargs.get('remote_user', None),
        module_path=['/data/.virtualenvs/small_platform/lib/python3.6/site-packages/ansible'],
        forks=kwargs.get('forks', 10),
        become=None,
        become_method=None,
        become_user=None,
        check=False,
        diff=False,
        timeout=kwargs.get('timeout', 10),
        syntax=None,
        start_at_task=None,
        extra_vars=kwargs.get('extra_vars', None),
        tags=kwargs.get('tags', ['all']),
        verbosity=kwargs.get('verbosity', 0),
        listtasks=kwargs.get('listtasks', None),
        listtags=kwargs.get('listtags', None),
        listhosts=kwargs.get('listhosts', None),
    )
    code, playbooks = check_file_exists(playbooks, new_dir='/data/ansible/playbook')
    if code == 1:
        return playbooks

    code, sources = check_file_exists(sources, new_dir='/data/ansible/playbook/hosts')
    if code == 1:
        return sources

    loader = DataLoader()

    inventory = InventoryManager(loader=loader, sources=sources)

    variable_manager = VariableManager(loader=loader, inventory=inventory)

    passwords = dict(vault_pass='secret')

    pbex = PlaybookExecutor(playbooks=(playbooks, ), inventory=inventory, variable_manager=variable_manager,
                            loader=loader, passwords=passwords)
    results_callback = JSONCallback()
    if pbex._tqm:
        pbex._tqm._stdout_callback = results_callback
    pbex.run()
    results = dict(
        host_ok=results_callback.host_ok,
        host_failed=results_callback.host_failed,
        host_unreachable=results_callback.host_unreachable,
        host_skipped=results_callback.host_skipped
    )

    host_failed, host_unreachable = results['host_failed'], results['host_unreachable']
    if host_failed or host_unreachable:
        return 1, {'host_failed': host_failed, 'host_unreachable': host_unreachable}
    else:
        return 0, results



if __name__ == '__main__':
    # code, results = playbook('/data/ansible/playbook/filebeat.yml', '/data/ansible/playbook/hosts/web.hosts',
    #          extra_vars=['hosts=172.25.161.21,172.24.161.21 logs={{ pt_web_logs }} project_name=pt_web_logs', ],
    #          tags=['template_filebeat_config', ])
    code, results = playbook('test.yml', 'web.hosts', extra_vars=['hosts=172.29.161.150'], tags=['temp_config_loop', 'create_dir_loop'])
    playbook('filebeat.yml', 'syslog_test.hosts',
             extra_vars=['hosts=172.24.161.21,172.24.161.22 logs={{ syslog_test }} project_name=syslog_test'],
             tags=['template_filebeat_config'])
    if code == 1:
        host_failed = results['host_failed']
        host_unreachable = results['host_unreachable']

        for item in host_failed:
            for host, result in item.items():
                    print(f'{host} >>> {result._result}')

        for item in host_unreachable:
            for host, result in item.items():
                    print(f'{host} >>> {result._result}')
