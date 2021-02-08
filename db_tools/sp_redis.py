import json
from redis import StrictRedis
from collections import Iterable

class ExecRedis(object):
    def __init__(self, host='127.0.0.1', port=6379, db=0, **kwargs):
        self.host = host
        self.port = port
        self.db = db
        self.decode_responses = kwargs.pop('decode_responses', False)
        self.conn = StrictRedis(host=self.host, port=self.port, db=self.db, decode_responses=self.decode_responses, **kwargs)

    def json_set(self, name, data):
        if isinstance(data, Iterable):
            data = json.dumps(data)
        self.conn.set(name, data)

    def json_get(self, name):
        data = self.conn.get(name)
        try:
            res = eval(data)
            return {
                'code': 0,
                'results': res
            }
        except Exception as e:
            return {
                'code': 1,
                'results': str(e)
            }

rediscli = ExecRedis(host='172.28.161.150', port=6588, decode_responses=True)


if __name__ == '__main__':
    pass
