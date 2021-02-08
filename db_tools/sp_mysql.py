import MySQLdb
from MySQLdb.cursors import DictCursor
from MySQLdb._exceptions import OperationalError

from mix_tools.check import check_ipv4_is_valid


class ExecMysql(object):
    """
    :param type cursorclass :
        class object, used to create cursors (keyword only)
    """

    def __init__(self, **kwargs):
        for item in ['user', 'password']:
            assert kwargs.get(item, None), '未提供参数<%s>' % item
        self.host = kwargs.get('host', '127.0.0.1')
        self.port = kwargs.get('port', 3306)
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.database = kwargs.get('database', '')
        self.connect_timeout = kwargs.get('connect_timeout', 5)

        self.conn = MySQLdb.connect(host=self.host, port=int(self.port), user=self.user, password=self.password,
                                    database=self.database, charset='utf8', cursorclass=DictCursor, connect_timeout=self.connect_timeout)
        self.cur = self.conn.cursor()

    def execute_raw_sql(self, sql):
        self.cur.execute(sql)

    def fetch_one(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchone()

    def fetch_all(self, sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    def get_hosts(self, table='assets_info'):
        sql = 'select * from %s' % table
        return self.fetch_all(sql)

    @property
    def show_master_status(self):
        sql = 'show master status'
        return self.fetch_one(sql)

    @property
    def show_slave_status(self):
        sql = 'show slave status'
        ret = self.fetch_one(sql)
        if ret:
            results = {
                'master_host': ret['Master_Host'],
                'master_user': ret['Master_User'],
                'master_port': ret['Master_Port'],
                'master_log_file': ret['Master_Log_File'],
                'read_master_log_pos': ret['Read_Master_Log_Pos'],
                'slave_io_running': ret['Slave_IO_Running'],
                'slave_sql_running': ret['Slave_SQL_Running'],
                'exec_master_log_pos': ret['Exec_Master_Log_Pos'],
                'last_io_errno': ret['Last_IO_Errno'],
                'last_io_error': ret['Last_IO_Error'],
                'last_sql_errno': ret['Last_SQL_Errno'],
                'last_sql_error': ret['Last_SQL_Error'],
            }
            if ret['Read_Master_Log_Pos'] > ret['Exec_Master_Log_Pos']:
                return {
                    'code': 1,
                    'msg': '同步有延迟',
                    'results': results
                }
            elif ret['Slave_SQL_Running'].lower() != 'yes' and ret['Slave_IO_Running'].lower() != 'yes':
                return {
                    'code': 2,
                    'msg': '同步有异常',
                    'results': results
                }
            else:
                return {
                    'code': 0,
                    'msg': '同步正常',
                    'results': results
                }
        else:
            return {
                'code': 1,
                'msg': '此实例无主从',
                'results': 'Empty set!'
            }

    @property
    def show_read_only(self):
        sql = 'show global variables like "read_only"'
        ret = self.fetch_one(sql)
        return {ret['Variable_name']: ret['Value'].lower()}

    def set_read_only(self, value='off'):
        sql = 'set global read_only=%s' % value
        self.execute_raw_sql(sql)
        return self.show_read_only

    def set_master_slave(self, **config):
        for item in ['host', 'port', 'user', 'password', 'log_file', 'log_pos']:
            assert config.get(item, None), '未提供参数<%s>' % item
        sql = f'''change master to master_host="{config['host']}",master_port={config['port']},master_user="{config['user']}",\
master_password="{config['password']}",master_log_file="{config['log_file']}",master_log_pos={config['log_pos']};'''
        self.execute_raw_sql(sql)

    def start_slave(self):
        """
        :return: slave infomation
        """
        sql = 'start slave'
        self.execute_raw_sql(sql)
        return self.show_slave_status

    def stop_slave(self, reset=False):
        """
        :param reset: 如果True，停止从并清空
        :return: slave infomation
        """
        sql = 'stop slave'
        self.execute_raw_sql(sql)
        if reset:
            sql = 'reset slave all'
            self.execute_raw_sql(sql)
        return self.show_slave_status

    def close(self):
        self.cur.close()
        self.conn.close()


def check_mysql_connection(**kwargs):
    for item in ['host', 'port', 'user', 'password']:
        assert kwargs.get(item, None), '未提供参数<%s>' % item
    try:
        ExecMysql(**kwargs)
        return {'code': 0, 'msg': 'connect success!'}
    except OperationalError as e:
        return {'code': 1, 'msg': e.args[1]}


def check_master_slave(master_slave, **config):
    """
    检测是否为主从复制
    :param master_slave: 元组，0主 1从, example: (10.20.50.83:3308, 10.20.50.93:3308)
    :param config: 用户密码信息
    :return:
    """
    for item in ['user', 'password']:
        assert config.get(item, None), '未提供参数<%s>' % item
    slave_em = ExecMysql(host=handle_ip_port(master_slave[1])[0], port=handle_ip_port(master_slave[1])[1],
                           user=config['user'], password=config['password'])
    master_host, master_port = handle_ip_port(master_slave[0])
    slave_info = slave_em.show_slave_status
    if isinstance(slave_info['results'], dict) and slave_info['results']['master_host'] == master_host and \
            slave_info['results']['master_port'] == master_port:
        return {
            'code': 0,
            'msg': '主从复制正常',
            'results': f'[{master_slave[0]}] 和 [{master_slave[1]}]是主从关系'
        }
    else:
        return {
            'code': 1,
            'msg': "主从复制异常",
            'results': f'[{master_slave[0]}] 和 [{master_slave[1]}]不是主从关系'
        }


def handle_ip_port(content):
    # 172.28.161.21:3306，返回(ip, port)元组
    assert ':' in content, "%s must contain ':'" % content
    ip, port = content.split(':')
    assert check_ipv4_is_valid(ip), "%s is invalid" % ip
    return ip, int(port)


def switch_master_slave(old_master_slave, new_master_slave, **replica):
    """
    数据库主从新建操作
    :param old_master_slave: 元组，0主 1从, example: (10.20.50.83:3308, 10.20.50.93:3308)
    :param new_master_slave: 元组，0主 1从, example: (10.20.50.93:3318, 10.20.50.83:3318)
    :param replica: 用户密码信息
    :return:
    """
    for item in ['user', 'password', 'replica_user', 'replica_password']:
        assert replica.get(item, None), '未提供参数<%s>' % item
    old_master = ExecMysql(host=handle_ip_port(old_master_slave[0])[0], port=handle_ip_port(old_master_slave[0])[1],
                           user=replica['user'], password=replica['password'])
    old_slave = ExecMysql(host=handle_ip_port(old_master_slave[1])[0], port=handle_ip_port(old_master_slave[1])[1],
                          user=replica['user'], password=replica['password'])
    new_master = ExecMysql(host=handle_ip_port(new_master_slave[0])[0], port=handle_ip_port(new_master_slave[0])[1],
                           user=replica['user'], password=replica['password'])
    new_slave = ExecMysql(host=handle_ip_port(new_master_slave[1])[0], port=handle_ip_port(new_master_slave[1])[1],
                          user=replica['user'], password=replica['password'])
    switch_log = [f'> {old_master_slave}<=>{new_master_slave} 只读设置ON并开始主从新建']
    # 1、全部设置只读
    for item in [old_master, old_slave, new_master, new_slave]:
        item.set_read_only(value='on')
    # 2、记录新、旧主master infomation
    old_master_info = old_master.show_master_status
    switch_log.append(f'操作: 查看主信息, 角色: 旧主, Host: {old_master_slave[0]}, 信息: log_file: {old_master_info["File"]}, '
                      f'log_pos: {old_master_info["Position"]}')
    new_master_info = new_master.show_master_status
    switch_log.append(f'操作: 查看主信息, 角色: 新主, Host: {new_master_slave[0]}, 信息: log_file: {new_master_info["File"]}, '
                      f'log_pos: {new_master_info["Position"]}')
    # 3、检查原有主从同步情况，正常情况执行主从切换，不正常恢复
    old_replica_status = old_slave.show_slave_status
    if old_replica_status['code'] == 0:
        # 4、停止旧主从
        ret = old_slave.stop_slave(reset=True)
        switch_log.append(f'操作: 停止主从复制, 角色: 旧从, Host: {old_master_slave[1]}, 信息: {ret["msg"]}')
        # 5、建立新主从
        new_slave.set_master_slave(host=handle_ip_port(new_master_slave[0])[0], port=handle_ip_port(new_master_slave[0])[1],
                                   user=replica['replica_user'], password=replica['replica_password'],
                                   log_file=new_master_info['File'], log_pos=new_master_info['Position'])
        ret = new_slave.start_slave()
        switch_log.append(f'操作: 建立主从复制, 角色: 新从, Host: {new_master_slave[1]}, 信息: {ret["results"]}')
        ret.update(results='\n'.join(switch_log))
        return ret
    else:
        switch_log.append(f'操作: 查看从信息, 角色: 旧从, Host: {old_master_slave[1]}, 信息: {old_replica_status["msg"]} {old_replica_status["results"]}')
        return {
            'code': 1,
            'msg': '主从切换失败',
            'results': '\n'.join(switch_log)
        }


def cut_master_slave(slave_host, **replica):
    """
    数据库主从切断操作
    :param slave_host: 10.20.50.93:3308
    :param replica: 用户密码信息
    :return:
    """
    for item in ['user', 'password']:
        assert replica.get(item, None), '未提供参数<%s>' % item
    slave_em = ExecMysql(host=handle_ip_port(slave_host)[0], port=handle_ip_port(slave_host)[1],
                          user=replica['user'], password=replica['password'])
    cut_logs = [f'> {slave_host} 开始切断主从']
    ret = slave_em.stop_slave(reset=True)
    cut_logs.append(f'操作: 切断主从复制, 角色: 从库, Host: {slave_host[1]}, 信息: {ret["results"]}')
    if ret['results'] == 'Empty set!':
        return {'code': 0, 'msg': '主从切断成功', 'results': '\n'.join(cut_logs)}
    else:
        return {'code': 1, 'msg': '主从切断失败', 'results': '\n'.join(cut_logs)}



if __name__ == '__main__':
    pass
