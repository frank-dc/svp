from .alidns import describe_sub_domain_records, set_domain_record_status
from .dnspod import RecordList, RecordStatus
from tool.models import ExtranetIP


def retrieve_records_for_domain(domain):
    """
    根据域名获取解析记录
    :param domain: pay.sdk.mobileztgame.com
    :return:
    """
    ali_domain = ['mobileztgame.com', 'mztgame.com']
    dnspod_domain = ['ztinfoga.com', ]
    domain_split = domain.split('.')
    domain_suffix = '.'.join(domain_split[-2:])
    domain_prefix = '.'.join(domain_split[:-2])

    if domain_suffix in ali_domain:
        try:
            results = describe_sub_domain_records(domain_prefix, domain_name=domain_suffix)
            raw_records = results['DomainRecords']['Record']
            records = [{
                'name': item.get('RR', None),
                'status': item.get('Status', '').lower(),
                'value': item.get('Value', None),
                'id': item.get('RecordId', None)
            } for item in raw_records]
            return {
                'code': 0,
                'results': records
            }
        except Exception as e:
            return {
                'code': 1,
                'results': str(e)
            }
    elif domain_suffix in dnspod_domain:
        try:
            rl = RecordList(domain=domain_suffix, sub_domain=domain_prefix, length=500, record_type='A')
            results = rl()
            raw_records = results['records']
            records = [{
                'name': item.get('name', None),
                'status': item.get('status', None),
                'id': item.get('id', None),
                'value': item.get('value', None)
            } for item in raw_records]
            return {
                'code': 0,
                'results': records
            }
        except Exception as e:
            return {
                'code': 1,
                'results': str(e)
            }
    else:
        return {
            'code': 1,
            'results': '未知域名%s所属平台["万网", "DNSPod"]' % domain_suffix
        }


def domain_records_info(domain):
    """
    给域名记录加上机房、线路信息
    :param domain:
    :return:
    """
    ret = retrieve_records_for_domain(domain)
    if ret['code'] == 0:
        handle = []
        for item in ret['results']:
            eip_ins = ExtranetIP.objects.get(ip=item['value'])
            item.update(idc=eip_ins.idc.name, line=eip_ins.get_line_display())
            handle.append(item)
        return {
            'code': 0,
            'results': handle
        }
    else:
        return ret


def set_domain_records_status(domain, status, idc=None, line=None):
    """
    对域名所在机房或线路的解析做启停
    :param domain:
    :param status: enable or disable
    :param idc: 机房名称
    :param line: 线路名称
    :return:
    """
    ret = domain_records_info(domain)
    ali_domain = ['mobileztgame.com', 'mztgame.com']
    dnspod_domain = ['ztinfoga.com', ]
    domain_split = domain.split('.')
    domain_suffix = '.'.join(domain_split[-2:])

    if ret['code'] == 0:
        records = ret['results']
        try:
            for item in records:
                if item['idc'] == idc and domain_suffix in ali_domain:
                    set_domain_record_status(item['id'], status)
                elif item['idc'] == idc and domain_suffix in dnspod_domain:
                    RecordStatus(domain=domain_suffix, record_id=item['id'], status=status)()
                if item['line'] == line and domain_suffix in ali_domain:
                    set_domain_record_status(item['id'], status)
                elif item['line'] == line and domain_suffix in dnspod_domain:
                    RecordStatus(domain=domain_suffix, record_id=item['id'], status=status)()
            return {
                'code': 0,
                'results': '设置成功'
            }
        except Exception as e:
            return {
                'code': 1,
                'results': str(e)
            }
    else:
        return ret



if __name__ == '__main__':
    pass
