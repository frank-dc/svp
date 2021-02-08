import paramiko

class SSHClient(object):
    """
    使用https://github.com/paramiko/paramiko连接主机远程执行操作
    """
    def __init__(self, **kwargs):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 22)
        self.user = kwargs.get('user', 'root')
        self.key_filename = kwargs.get('key_filename', 'no key')
        self.password = kwargs.get('password', 'no pass')
        assert not (self.key_filename == 'no key' and self.password == 'no pass'), 'must provide one argument ' \
                                                                             'between of <password> and <key_filename>'
        if self.key_filename != 'no key':
            self.ssh.connect(self.host, port=self.port, username=self.user, key_filename=self.key_filename)
        else:
            self.ssh.connect(self.host, port=self.port, username=self.user, password=self.password)
        self.context = None

    def exec_command(self, command):
        self.context = self.ssh.exec_command(command)

    def fetch_stdout(self):
        errors = self.fetch_stderr()
        stdouts = self.context[1].read().decode('utf-8')
        if errors:
            return {
                'code': 1,
                'results': errors
            }
        else:
            return {
                'code': 0,
                'results': stdouts
            }

    def fetch_stderr(self):
        return self.context[2].read().decode('utf-8')

    def close(self):
        self.ssh.close()


def remote_command(host, cmd):
    ssh = SSHClient(host=host, key_filename='/root/.ssh/id_rsa')
    ssh.exec_command(cmd)
    fetch_ret = ssh.fetch_stdout()
    if fetch_ret['code'] == 1:
        return {
            'code': 1,
            'msg': '# 在%s执行%s失败' % (host, cmd),
            'results': fetch_ret['results']
        }
    else:
        return {
            'code': 0,
            'msg': '# 在%s执行%s成功' % (host, cmd),
            'results': fetch_ret['results']
        }


if __name__ == '__main__':
    cmd = 'kubectl describe node 172.28.200.9 | grep cpu | tail -1'
    results = remote_command('172.28.200.9', cmd)
    print(results['results'])