#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
import json
import re


class ApiCn:
    def __init__(self, id=None, token=None, **kwargs):
        self.base_url = "https://dnsapi.cn"
        self.params = dict(
            login_token="%s,%s" % (id, token),
            format="json"
        )
        self.params.update(kwargs)
        self.path = None

    def request(self, **kwargs):
        self.params.update(kwargs)
        if not self.path:
            """Class UserInfo will auto request path /User.Info."""
            name = re.sub(r'([A-Z])', r'.\1', self.__class__.__name__)
            self.path = "/" + name[1:]
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json",
                   "User-Agent": "dnspod-python/0.01 (im@chuangbo.li; DNSPod.CN API v2.8)"}
        r = requests.post(self.base_url + self.path, data=self.params, headers=headers)
        ret = r.json()
        if ret.get("status", {}).get("code") == "1":
            return ret
        else:
            raise Exception(ret)

    __call__ = request


class InfoVersion(ApiCn):
    pass


class UserDetail(ApiCn):
    pass


class UserInfo(ApiCn):
    pass


class UserLog(ApiCn):
    pass


# domain基类
class _DomainApiBase(ApiCn):
    def __init__(self, domain, **kwargs):
        kwargs.update(dict(domain=domain))
        super(_DomainApiBase, self).__init__(**kwargs)


class DomainCreate(_DomainApiBase):
    pass


class DomainId(_DomainApiBase):
    pass


class DomainList(ApiCn):
    pass


class DomainRemove(_DomainApiBase):
    pass


class DomainStatus(_DomainApiBase):
    def __init__(self, status, **kwargs):
        kwargs.update(dict(status=status))
        super(DomainStatus, self).__init__(**kwargs)


class DomainInfo(_DomainApiBase):
    pass


class DomainLog(_DomainApiBase):
    pass


class RecordType(ApiCn):
    def __init__(self, domain_grade, **kwargs):
        kwargs.update(dict(domain_grade=domain_grade))
        super(RecordType, self).__init__(**kwargs)


class RecordLine(ApiCn):
    def __init__(self, domain_grade=None, **kwargs):
        kwargs.update(dict(domain_grade=domain_grade))
        super(RecordLine, self).__init__(**kwargs)


class RecordCreate(_DomainApiBase):
    def __init__(self, sub_domain, record_type, record_line, value, ttl, mx=None, **kwargs):
        kwargs.update(dict(
            sub_domain=sub_domain,
            record_type=record_type,
            record_line=record_line,
            value=value,
            ttl=ttl,
        ))
        if mx:
            kwargs.update(dict(mx=mx))
        super(RecordCreate, self).__init__(**kwargs)


class RecordModify(RecordCreate):
    def __init__(self, record_id, **kwargs):
        kwargs.update(dict(record_id=record_id))
        super(RecordModify, self).__init__(**kwargs)


class RecordList(_DomainApiBase):
    pass


# record基类
class _RecordBase(_DomainApiBase):
    def __init__(self, record_id, **kwargs):
        kwargs.update(dict(record_id=record_id))
        super(_RecordBase, self).__init__(**kwargs)


class RecordRemove(_RecordBase):
    pass


class RecordDdns(_DomainApiBase):
    def __init__(self, record_id, sub_domain, record_line, **kwargs):
        kwargs.update(dict(
            record_id=record_id,
            sub_domain=sub_domain,
            record_line=record_line
        ))
        super(RecordDdns, self).__init__(**kwargs)


class RecordStatus(_RecordBase):
    def __init__(self, status, **kwargs):
        kwargs.update(dict(status=status))
        super(RecordStatus, self).__init__(**kwargs)


class RecordInfo(_RecordBase):
    pass


if __name__ == "__main__":
    pass
