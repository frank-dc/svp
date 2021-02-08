from aliyunsdkcore.client import AcsClient
from aliyunsdkalidns.request.v20150109 import DescribeDomainInfoRequest
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordInfoRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import SetDomainRecordStatusRequest
from aliyunsdkalidns.request.v20150109 import DescribeSubDomainRecordsRequest
import json
import sys
import os
import redis


def _client(key, secret):
    access_key_id = key
    access_key_secret = secret
    client = AcsClient(access_key_id, access_key_secret)
    return client


def describe_domain_info(domain_name):
    """
    域名信息
    :param domain_name:
    :return:
    """
    request = DescribeDomainInfoRequest.DescribeDomainInfoRequest()
    request.set_DomainName(domain_name)
    client = _client()
    result = client.do_action_with_exception(request)
    result_dict = json.loads(result)
    return result_dict


def describe_domain_records(domain_name, type="A"):
    """
    域名的所有A记录
    :param domain_name:
    :param type:
    :return:
    """
    request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    request.set_DomainName(domain_name)
    request.set_PageSize(500)
    request.set_TypeKeyWord(type)
    request.set_accept_format("json")
    client = _client()
    result = client.do_action_with_exception(request)  # bytes 类型
    result_dict = json.loads(result)
    return result_dict


def describe_sub_domain_records(sub_domain, domain_name="mobileztgame.com", type="A"):
    """
    子域名的所有A记录
    :param sub_domain:
    :param domain_name:
    :param type:
    :return:
    """
    request = DescribeSubDomainRecordsRequest.DescribeSubDomainRecordsRequest()
    request.set_SubDomain(sub_domain + "." + domain_name)
    request.set_Type(type)
    client = _client()
    result = client.do_action_with_exception(request)
    result_dict = json.loads(result)
    return result_dict


def describe_domain_record_info(record_id):
    """
    通过record_id获取一条特定记录
    :param record_id:
    :return:
    """
    request = DescribeDomainRecordInfoRequest.DescribeDomainRecordInfoRequest()
    request.set_RecordId(record_id)
    client = _client()
    result = client.do_action_with_exception(request)
    result_dict = json.loads(result)
    return result_dict


def update_domain_recored(record_id, rr, type, value, ttl=600, line="default"):
    """
    修改域名记录
    :param record_id:
    :param rr:
    :param type:
    :param value:
    :param ttl:
    :param line:
    :return:
    """
    request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    request.set_RecordId(record_id)
    request.set_RR(rr)
    request.set_Type(type)
    request.set_Value(value)
    request.set_TTL(ttl)
    request.set_Line(line)
    client = _client()
    result = client.do_action_with_exception(request)
    result_dict = json.loads(result)
    return result_dict


def set_domain_record_status(record_id, status):
    """
    启用/暂停一条特定的记录
    :param record_id:
    :param status:
    :return:
    """
    request = SetDomainRecordStatusRequest.SetDomainRecordStatusRequest()
    request.set_RecordId(record_id)
    request.set_Status(status.capitalize())
    client = _client()
    result = client.do_action_with_exception(request)
    result_dict = json.loads(result)
    return result_dict


if __name__ == '__main__':
    pass
