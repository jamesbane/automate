# Python
import io
import os
import re
import csv
import sys
import time
import base64
import datetime
import traceback
from collections import OrderedDict

# Django
from django.utils import timezone
from django.conf import settings

# Application
from tools.models import Process, ProcessContent

# Third Party
from lib.pyutil.util import Util
from lib.pybw.broadworks import BroadWorks, Nil



class BroadWorksLab:
    _bw = None

    def __init__(self, process):
        self._process = process
        self._bw = BroadWorks(url=self._process.platform.uri,
                              username=self._process.platform.username,
                              password=self._process.platform.password)
        self._bw.LoginRequest14sp4()

    def parse_response(self, response, level):
        content = io.StringIO()
        content.write('{}\n'.format(response['type']))
        if response['type'] == 'c:ErrorResponse':
            if 'summaryEnglish' in response['data'] and 'errorCode' in response['data']:
                content.write('{}[{}] {}\n'.format('    '*(level+1), response['data']['errorCode'], response['data']['summaryEnglish']))
            elif 'summaryEnglish' in response['data']:
                content.write('{}{}\n'.format('    '*level, response['data']['summaryEnglish']))
            elif 'summary' in response['data'] and 'errorCode' in response['data']:
                content.write('{}[{}] {}\n'.format('    '*(level+1), response['data']['errorCode'], response['data']['summary']))
            elif 'summary' in response['data']:
                content.write('{}{}\n'.format('    '*(level+1), response['data']['summary']))
        rval = content.getvalue()
        content.close()
        return rval

    def rebuild(self, provider, groups, users):
        content = io.StringIO()
        content.write("Reset Existing Devices\n")
        level=1
        for user in users:
            content.write("{}GroupAccessDeviceResetRequest(serviceProviderId={}, groupId={}, deviceName={}) ".format('    '*level, provider['id'], user['group_id'], user['user_id'])),
            resp = self._bw.GroupAccessDeviceResetRequest(serviceProviderId=provider['id'], groupId=user['group_id'], deviceName=user['user_id'])
            content.write(self.parse_response(resp, level))
        content.write('\n')

        content.write("Retrieve Defaults\n")
        content.write("{}ServiceProviderServiceGetAuthorizationListRequest('00001') ".format('    '*level)),
        resp = self._bw.ServiceProviderServiceGetAuthorizationListRequest('00001')
        content.write(self.parse_response(resp, level))
        Lab_service_authorization_list = resp['data']
        content.write("{}GroupServiceGetAuthorizationListRequest('00001', 'IP Voice Phone System') ".format('    '*level)),
        resp = self._bw.GroupServiceGetAuthorizationListRequest('00001', 'IP Voice Phone System')
        Lab_group_service_auth = resp['data']
        content.write(self.parse_response(resp, level))
        content.write('\n')

        content.write("Delete Groups & Provider\n")
        for group in groups:
            content.write("{}GroupDeleteRequest({}, {}) ".format('    '*level, provider['id'], group['id'])),
            resp = self._bw.GroupDeleteRequest(provider['id'], group['id'])
            content.write(self.parse_response(resp, level))
        content.write("{}ServiceProviderDeleteRequest({}) ".format('    '*level, provider['id'])),
        resp = self._bw.ServiceProviderDeleteRequest(provider['id'])
        content.write(self.parse_response(resp, level))
        content.write('\n')

        content.write("Enterprise: {}\n".format(provider['id']))
        # Enterprise
        content.write("{}ServiceProviderAddRequest13mp2({}, {}, enterprise=True) ".format('    '*level, provider['id'], provider['description'])),
        resp = self._bw.ServiceProviderAddRequest13mp2(provider['id'], provider['description'], enterprise=True)
        content.write(self.parse_response(resp, level))
        # assign numbers
        content.write("{}ServiceProviderDnAddListRequest({}, phoneNumber={{...}}) ".format('    '*level, provider['id'])),
        resp = self._bw.ServiceProviderDnAddListRequest(provider['id'], phoneNumber=provider['numbers'])
        content.write(self.parse_response(resp, level))
        # authorized services
        authorization_list = {'groupServiceAuthorization': list(), 'userServiceAuthorization': list()}
        for d in Lab_service_authorization_list['groupServicesAuthorizationTable']:
            if d['Authorized'] != 'true':
                continue
            data = OrderedDict()
            data['serviceName'] = d['Service Name']
            if d['Limited'] == 'Unlimited':
                data['authorizedQuantity'] = {'unlimited': True}
            else:
                data['authorizedQuantity'] = {'quantity': d['Quantity']}
            authorization_list['groupServiceAuthorization'].append(data)
        for d in Lab_service_authorization_list['userServicesAuthorizationTable']:
            if d['Authorized'] != 'true':
                continue
            data = OrderedDict()
            data['serviceName'] = d['Service Name']
            if d['Limited'] == 'Unlimited':
                data['authorizedQuantity'] = {'unlimited': True}
            else:
                data['authorizedQuantity'] = {'quantity': d['Quantity']}
            authorization_list['userServiceAuthorization'].append(data)
        content.write("{}ServiceProviderServiceModifyAuthorizationListRequest({}, ...) ".format('    '*level, provider['id'])),
        resp = self._bw.ServiceProviderServiceModifyAuthorizationListRequest(provider['id'], **authorization_list)
        content.write(self.parse_response(resp, level))

        # service packs
        content.write("{}ServiceProviderServicePackGetListRequest('00001') ".format('    '*level)),
        resp = self._bw.ServiceProviderServicePackGetListRequest('00001')
        content.write(self.parse_response(resp, level))
        Lab_service_pack_list = resp['data']['servicePackName']
        for service_pack_name in Lab_service_pack_list:
            content.write("{}ServiceProviderServicePackGetDetailListRequest('00001', {}) ".format('    '*level, service_pack_name)),
            resp = self._bw.ServiceProviderServicePackGetDetailListRequest('00001', service_pack_name)
            content.write(self.parse_response(resp, level))
            service_pack_detail = resp['data']

            services = list()
            for service in service_pack_detail['userServiceTable']:
                # "Service", "Authorized" "Allocated" and "Available".
                services.append(service['Service'])

            content.write("{}ServiceProviderServicePackAddRequest({}, {}, ...) ".format('    '*level, provider['id'], service_pack_name)),
            resp = self._bw.ServiceProviderServicePackAddRequest(provider['id'],
                                                                 service_pack_detail['servicePackName'],
                                                                 service_pack_detail['isAvailableForUse'],
                                                                 service_pack_detail['servicePackQuantity'],
                                                                 serviceName=services)
            content.write(self.parse_response(resp, level))
        content.write('\n')

        for group in groups:
            content.write("Group: {}::{}\n".format(provider['id'], group['id']))
            content.write("{}GroupAddRequest({}, {}, userLimit='999999', groupName={}) ".format('    '*level, provider['id'], group['id'], group['name'])),
            resp = self._bw.GroupAddRequest(provider['id'], group['id'], userLimit='999999', groupName=group['name'])
            content.write(self.parse_response(resp, level))
            content.write("{}GroupDnAssignListRequest({}, {}, phoneNumber={{...}}) ".format('    '*level, provider['id'], group['id'])),
            resp = self._bw.GroupDnAssignListRequest(provider['id'], group['id'], phoneNumber=group['numbers'])
            content.write(self.parse_response(resp, level))
            content.write("{}GroupModifyRequest({}, {}, callingLineIdPhoneNumber={}) ".format('    '*level, provider['id'], group['id'], group['number'])),
            resp = self._bw.GroupModifyRequest(provider['id'], group['id'], callingLineIdPhoneNumber=group['number'])
            content.write(self.parse_response(resp, level))
            service_auth = {'servicePackAuthorization': list(), 'groupServiceAuthorization': list(), 'userServiceAuthorization': list()}
            for d in Lab_group_service_auth['servicePacksAuthorizationTable']:
                if d['Authorized'] != 'true':
                    continue
                data = OrderedDict()
                data['servicePackName'] = d['Service Pack Name']
                if d['Allowed'] == 'Unlimited':
                    data['authorizedQuantity'] = {'unlimited': True}
                else:
                    data['authorizedQuantity'] = {'quantity': d['Quantity']}
                service_auth['servicePackAuthorization'].append(data)
            for d in Lab_group_service_auth['groupServicesAuthorizationTable']:
                if d['Authorized'] != 'true':
                    continue
                data = OrderedDict()
                data['serviceName'] = d['Service Name']
                if d['Allowed'] == 'Unlimited':
                    data['authorizedQuantity'] = {'unlimited': True}
                else:
                    data['authorizedQuantity'] = {'quantity': d['Quantity']}
                service_auth['groupServiceAuthorization'].append(data)
            for d in Lab_group_service_auth['userServicesAuthorizationTable']:
                if d['Authorized'] != 'true':
                    continue
                data = OrderedDict()
                data['serviceName'] = d['Service Name']
                if d['Allowed'] == 'Unlimited':
                    data['authorizedQuantity'] = {'unlimited': True}
                else:
                    data['authorizedQuantity'] = {'quantity': d['Quantity']}
                service_auth['userServiceAuthorization'].append(data)

            content.write("{}GroupServiceModifyAuthorizationListRequest({}, {}, ...) ".format('    '*level, provider['id'], group['id'])),
            resp = self._bw.GroupServiceModifyAuthorizationListRequest(provider['id'], group['id'], **service_auth)
            content.write(self.parse_response(resp, level))
            for service_name in group['assigned_services']:
                content.write("{}GroupServiceAssignListRequest({}, {}, {}) ".format('    '*level, provider['id'], group['id'], service_name)),
                resp = self._bw.GroupServiceAssignListRequest(provider['id'], group['id'], service_name)
                content.write(self.parse_response(resp, level))
            orig_permissions = OrderedDict()
            orig_permissions['group'] = 'Allow'
            orig_permissions['local'] = 'Allow'
            orig_permissions['tollFree'] = 'Allow'
            orig_permissions['toll'] = 'Allow'
            orig_permissions['international'] = 'Disallow'
            orig_permissions['operatorAssisted'] = 'Allow'
            orig_permissions['chargeableDirectoryAssisted'] = 'Allow'
            orig_permissions['specialServicesI'] = 'Allow'
            orig_permissions['specialServicesII'] = 'Allow'
            orig_permissions['premiumServicesI'] = 'Allow'
            orig_permissions['premiumServicesII'] = 'Allow'
            orig_permissions['casual'] = 'Disallow'
            orig_permissions['urlDialing'] = 'Disallow'
            orig_permissions['unknown'] = 'Disallow'
            content.write("{}GroupOutgoingCallingPlanOriginatingModifyListRequest({}, {}, groupPermissions={{...}}) ".format('    '*level, provider['id'], group['id'])),
            resp = self._bw.GroupOutgoingCallingPlanOriginatingModifyListRequest(provider['id'], group['id'], groupPermissions=orig_permissions)
            content.write(self.parse_response(resp, level))
            redirect_permissions = OrderedDict()
            redirect_permissions['group'] = True
            redirect_permissions['local'] = True
            redirect_permissions['tollFree'] = True
            redirect_permissions['toll'] = True
            redirect_permissions['international'] = False
            redirect_permissions['operatorAssisted'] = False
            redirect_permissions['chargeableDirectoryAssisted'] = False
            redirect_permissions['specialServicesI'] = False
            redirect_permissions['specialServicesII'] = False
            redirect_permissions['premiumServicesI'] = False
            redirect_permissions['premiumServicesII'] = False
            redirect_permissions['casual'] = False
            redirect_permissions['urlDialing'] = False
            redirect_permissions['unknown'] = False
            content.write("{}GroupOutgoingCallingPlanRedirectingModifyListRequest({}, {}, groupPermissions={{...}}) ".format('    '*level, provider['id'], group['id'])),
            resp = self._bw.GroupOutgoingCallingPlanRedirectingModifyListRequest(provider['id'], group['id'], groupPermissions=redirect_permissions)
            content.write(self.parse_response(resp, level))
            content.write('\n')

        for user in users:
            content.write("    {}::{}: {}\n".format(user['group_id'], user['user_id'], user['device_type']))
            content.write("{}GroupAccessDeviceAddRequest14({}, {}, {}, {}, username={}, password='8675309') ".format('    '*(level+1), provider['id'], user['group_id'], user['user_id'], user['device_type'], user['device_username'])),
            resp = self._bw.GroupAccessDeviceAddRequest14(provider['id'], user['group_id'], user['user_id'], user['device_type'], username=user['device_username'], password='8675309')
            content.write(self.parse_response(resp, (level+1)))
            access_device_endpoint = OrderedDict()
            access_device_endpoint['accessDevice'] = OrderedDict()
            access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
            access_device_endpoint['accessDevice']['deviceName'] = user['user_id']
            access_device_endpoint['linePort'] = user['line_port']
            content.write("{}UserAddRequest17sp4({}, {}, {}, {}, {}, {}, {}, extension={}, password='1234aB!', accessDeviceEndpoint={{...}}) ".format('    '*(level+1), provider['id'], user['group_id'], user['user_id'], user['last_name'], user['first_name'], user['last_name'], user['first_name'], user['extension'])),
            resp = self._bw.UserAddRequest17sp4(provider['id'], user['group_id'], user['user_id'], user['last_name'], user['first_name'], user['last_name'], user['first_name'], extension=user['extension'], password='1234aB!', accessDeviceEndpoint=access_device_endpoint)
            content.write(self.parse_response(resp, (level+1)))
            content.write("{}GroupAccessDeviceModifyUserRequest({}, {}, {}, {}, True) ".format('    '*(level+1), provider['id'], user['group_id'], user['user_id'], user['line_port'])),
            resp = self._bw.GroupAccessDeviceModifyUserRequest(provider['id'], user['group_id'], user['user_id'], user['line_port'], True)
            content.write(self.parse_response(resp, (level+1)))
            content.write("{}UserServiceAssignListRequest({}, servicePackName={}) ".format('    '*(level+1), user['user_id'], user['service_pack'])),
            resp = self._bw.UserServiceAssignListRequest(user['user_id'], servicePackName=user['service_pack'])
            content.write(self.parse_response(resp, (level+1)))
            content.write('\n')

        # Shared Call and BLF
        content.write("    Shared Call Appearances and Busy Lamp Field\n")
        for user in users:
            # SCA
            for appearance in user['appearances']:
                access_device_endpoint = OrderedDict()
                access_device_endpoint['accessDevice'] = OrderedDict()
                access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
                access_device_endpoint['accessDevice']['deviceName'] = user['user_id']
                access_device_endpoint['linePort'] = appearance['line_port']
                content.write("{}UserSharedCallAppearanceAddEndpointRequest14sp2({}, {{...}}, isActive=True, allowOrigination=True, allowTermination=True) ".format('    '*(level+1), appearance['user_id'])),
                resp = self._bw.UserSharedCallAppearanceAddEndpointRequest14sp2(appearance['user_id'], access_device_endpoint, isActive=True, allowOrigination=True, allowTermination=True)
                content.write(self.parse_response(resp, (level+1)))

            # BLF
            if len(user['busy_lamp_field_users']):
                content.write("{}UserBusyLampFieldModifyRequest({}, listURI={}, monitoredUserIdList={{...}}) ".format('    '*(level+1), user['user_id'], '{}@telapexinc.com'.format(user['user_id']))),
                resp = self._bw.UserBusyLampFieldModifyRequest(user['user_id'], listURI='{}@telapexinc.com'.format(user['user_id']), monitoredUserIdList=user['busy_lamp_field_users'])
                content.write(self.parse_response(resp, (level+1)))
        content.write('\n')

        # Group Services
        content.write("Group Services\n")
        for group in groups:
            for service in group['service_instances']:
                if service['type'] == 'Hunt Group':
                    service_instance_profile = OrderedDict()
                    service_instance_profile['name'] = service['name']
                    service_instance_profile['callingLineIdLastName'] = service['clid_last_name']
                    service_instance_profile['callingLineIdFirstName'] = service['clid_first_name']
                    service_instance_profile['phoneNumber'] = service['number']
                    service_instance_profile['extension'] = service['extension']
                    service_instance_profile['password'] = '1234aB!'
                    service_instance_profile['callingLineIdPhoneNumber'] = service['clid_number']
                    content.write("{}GroupHuntGroupAddInstanceRequest19({}, {}, {}, ...) ".format('    '*level, provider['id'], group['id'], service['user_id'])),
                    resp = self._bw.GroupHuntGroupAddInstanceRequest19(provider['id'], group['id'], service['user_id'], service_instance_profile,
                                                                       policy='Simultaneous', huntAfterNoAnswer=False, noAnswerNumberOfRings=10, forwardAfterTimeout=False,
                                                                       forwardTimeoutSeconds=0, allowCallWaitingForAgents=False, useSystemHuntGroupCLIDSetting=True,
                                                                       includeHuntGroupNameInCLID=False, enableNotReachableForwarding=False, makeBusyWhenNotReachable=True,
                                                                       allowMembersToControlGroupBusy=False, enableGroupBusy=False, agentUserId=service['members'])
                    content.write(self.parse_response(resp, level))
        content.write('\n')

        rval = content.getvalue()
        content.close()
        return rval


#
# Local variables
#

#process = {
#    'platform': {
#        'url': 'https://onestreamnetworks.oci-us20.bcld.io/webservice/services/ProvisioningService?wsdl',
#        'username': 'JJjpextechpaas2@bwks.io',
#        'password': 'M50lPE6jHZKg5FhLZDwc',
#        'url': 'https://onestreamnetworks-sb.oci-us99.bcld.io/webservice/services/ProvisioningService?wsdl',
#        'username': 'jpexDev_fdcvoip.net@broadcloudpbx.net',
#        'password': '0!6~wFrzo2.ykcbi^+bkC!',
#        'id': '12332',
#        'seedSP': 'Fuse',
#        'seedGrp': 'Fuse Onboard Group',
#    }
#}

provider = {
    'id': '0301_Lab',
    'description': '301 Engineering Lab',
    'numbers': ['+1-704-555-1100', '+1-704-555-2100',],
}
groups = [
    {
        'id': '0301_LAB1',
        'name': '0301_LAB Engineering Lab 1',
        'number': '+1-704-555-1100',
        'numbers': ['+1-704-555-1100',],
        'assigned_services': ['Outgoing Calling Plan', 'Hunt Group'],
        'service_instances': ['']
    },
    {
        'id': '0301_LAB2',
        'name': '0301_LAB Engineering Lab 2',
        'number': '+1-704-555-2100',
        'numbers': ['+1-704-555-2100',],
        'assigned_services': ['Outgoing Calling Plan', 'Hunt Group'],
        'service_instances': ['']
    }
]
users = [
    # Group 1
    {
        'group_id': '0301_LAB1',
        'user_id': '0301_LAB1_1001',
        'device_type': 'Generic SIP Phone',
        'device_username': '301-1001',
        'first_name': '301 Lab',
        'last_name': '1001',
        'extension': '1001',
        'line_port': '0301_LAB__1_1001@lab.impulsevoip.net',
        'service_pack': 'IPVComplete',
        'assigned_services': ['Authentication'],
        'appearances': [
            { 'user_id': '' },
            { 'user_id': '' }],
        'busy_lamp_field_users': [''],
    },

    # Group 2
    {
        'group_id': '0301_LAB2',
        'user_id': '0301_LAB2_2001',
        'device_type': 'Generic SIP Phone',
        'device_username': '301-2001',
        'first_name': '301 Lab',
        'last_name': '2001',
        'extension': '2001',
        'line_port': '0301_LAB__2_2001@lab.impulsevoip.net',
        'service_pack': 'IPVComplete',
        'assigned_services': ['Authentication'],
        'appearances': [
            { 'user_id': '0301_LAB2_2002', 'line_port': '0301_LAB__2_2001_1@lab.impulsevoip.net' },
            { 'user_id': '0301_LAB2_2003', 'line_port': '0301_LAB__2_2001_2@lab.impulsevoip.net' }],
        'busy_lamp_field_users': ['0301_LAB2_2004', '0301_LAB2_2005', '0301_LAB2_2006',
                                  '0301_LAB2_2007', '0301_LAB2_2008', '0301_LAB2_2009',
                                  '0301_LAB2_2010'],
    },

]


def lab_rebuild(process_id):
    process = Process.objects.get(id=process_id)
    # Log Tab
    log_content = ProcessContent.objects.create(process=process, tab='Log', priority=1)
    dir_path = os.path.join(settings.PROTECTED_ROOT, 'process')
    filename_raw = '{}_{}'.format(process.id, 'log.txt')
    pathname_raw = os.path.join(dir_path, filename_raw)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    log_raw = open(pathname_raw, "w")
    log_content.raw.name = os.path.join('process', filename_raw)
    log_content.save()

    try:
        print("Process {}: {} -> {}".format(process_id, process.method, process.parameters))
        process.status = process.STATUS_RUNNING
        process.save(update_fields=['status'])
        bwl = BroadWorksLab(process)
        data = bwl.rebuild(provider, groups, users)
        log_raw.write(data)
        process.end_timestamp = timezone.now()
        process.status = process.STATUS_COMPLETED
        process.save(update_fields=['status', 'end_timestamp'])
    except Exception:
        process.status = process.STATUS_ERROR
        process.end_timestamp = timezone.now()
        process.exception = traceback.format_exc()
        process.save(update_fields=['status', 'exception', 'end_timestamp'])

    # Cleanup
    log_raw.close()
