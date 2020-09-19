# Python
import base64
import io
import os
import traceback
import csv
from collections import OrderedDict
from copy import deepcopy

# Django
from django.conf import settings
from django.utils import timezone

# Application
from tools.models import (Process, ProcessContent)

# Third Party
from lib.bw.broadworks import (BroadWorks, Nil)


class BroadWorkDeviceSwapPh2:
    _bw = None
    _content = io.StringIO()

    def __init__(self, process):
        self._process = process

        platform = self._process.platform_id
        self._bw = BroadWorks(url=platform.uri,
                              username=platform.username,
                              password=platform.password)
        self._bw.LoginRequest14sp4()

    def parse_response(self, response, level):
        content = io.StringIO()
        content.write('{}\n'.format(response['type']))
        if response['type'] == 'c:ErrorResponse':
            if 'summaryEnglish' in response['data'] and 'errorCode' in response['data']:
                content.write('{}[{}] {}\n'.format('    ' * (level + 1), response['data']['errorCode'],
                                                   response['data']['summaryEnglish']))
            elif 'summaryEnglish' in response['data']:
                content.write('{}{}\n'.format('    ' * level, response['data']['summaryEnglish']))
            elif 'summary' in response['data'] and 'errorCode' in response['data']:
                content.write('{}[{}] {}\n'.format('    ' * (level + 1), response['data']['errorCode'],
                                                   response['data']['summary']))
            elif 'summary' in response['data']:
                content.write('{}{}\n'.format('    ' * (level + 1), response['data']['summary']))
        rval = content.getvalue()
        content.close()
        return rval

    def logout(self):
        self._bw.LogoutRequest()

    def provider_check(self, provider_id, enterprise=False):
        if enterprise:
            resp0 = self._bw.ServiceProviderGetRequest17sp1(provider_id)
            provider_info = resp0['data']
            print(provider_info)
            if 'isEnterprise' in provider_info and provider_info['isEnterprise'] != True:
                raise Exception('Provider Id is not an Enterprise')
            elif 'isEnterprise' not in provider_info:
                raise Exception('Provider Id is not an Enterprise')

    def groups(self, provider_id):
        resp0 = self._bw.GroupGetListInServiceProviderRequest(serviceProviderId=provider_id)
        return resp0['data']['groupTable']

    # def device_swap_filter(self, group_id, device_types, department=None, provider_id=1003, **kwargs):
    def device_swap_filter(self, **kwargs):
        log = io.StringIO()
        summary = io.StringIO()
        level = kwargs.get('level', 0)
        device_types = self._process.parameters.get("device_types", [])
        log.write("{}Device Swap {}::{}::{}::{}\n".format(
            '    ' * level,
            self._process.parameters['provider_id'],
            self._process.parameters['group_id'],
            self._process.parameters['department'],
            device_types)
        )

        # get devices
        log.write('    {}Devices\n'.format('    ' * level))
        log.write('    {}GroupAccessDeviceGetListRequest({}, {}) '.format(
            '    ' * (level + 1),
            self._process.parameters['provider_id'],
            self._process.parameters['group_id'])
        )
        devices_response = self._bw.GroupAccessDeviceGetListRequest(
            self._process.parameters['provider_id'],
            self._process.parameters['group_id']
        )
        # devices_response = {"data": {"accessDeviceTable": [
        #     {"Device Name": "001565B61FC0", "Device Type": "Yealink-T42G", "Available Ports": 12, "Net Address": "",
        #      "MAC Address": "001565B61FC0", "Status": "Online", "Version": "Linksys/SPA2102-5.2.10",
        #      "Access Device External Id": ""},
        #     {"Device Name": "001565C92CCA", "Device Type": "Yealink-T46G", "Available Ports": 16, "Net Address": "",
        #      "MAC Address": "001565C92CCA", "Status": "Online", "Version": "eyeBeam release 3010n stamp 19039",
        #      "Access Device External Id": ""},
        #     {"Device Name": "6014991463", "Device Type": "Polycom_VVX150", "Available Ports": 2, "Net Address": None,
        #      "MAC Address": "", "Status": "Online", "Version": "", "Access Device External Id": ""},
        #     {"Device Name": "6014991464", "Device Type": "Polycom_VVX400", "Available Ports": 12, "Net Address": "",
        #      "MAC Address": "", "Status": "Online", "Version": "PolycomVVX-VVX_400-UA/5.9.5.0614_0004f28e5a79",
        #      "Access Device External Id": ""},
        #     {"Device Name": "6014991464_dt", "Device Type": "Polycom_VVX400", "Available Ports": 12, "Net Address": "",
        #      "MAC Address": "", "Status": "Online", "Version": "", "Access Device External Id": ""},
        #     {"Device Name": "6014991465", "Device Type": "Polycom_VVX500", "Available Ports": 16, "Net Address": "",
        #      "MAC Address": "", "Status": "Online", "Version": "PolycomVVX-VVX_500-UA/5.9.3.2857",
        #      "Access Device External Id": ""},
        #     {"Device Name": "6014991466", "Device Type": "Polycom_VVX400", "Available Ports": 12, "Net Address": "",
        #      "MAC Address": "", "Status": "Online", "Version": "Z 3.9.32144 r32121",
        #      "Access Device External Id": ""},
        #     {"Device Name": "6014991467", "Device Type": "Polycom_VVX300", "Available Ports": 6, "Net Address": "",
        #      "MAC Address": "", "Status": "Online", "Version": "",
        #      "Access Device External Id": "PolycomVVX-VVX_311-UA/5.9.3.2857"},
        #     {"Device Name": "6014991468", "Device Type": "Polycom_VVX500", "Available Ports": 16, "Net Address": "",
        #      "MAC Address": "", "Status": "Online", "Version": "Z 3.9.32144 r32121",
        #      "Access Device External Id": ""},
        #     {"Device Name": "Polycom VVX150", "Device Type": "Polycom_VVX150", "Available Ports": 2, "Net Address": "",
        #      "MAC Address": "", "Status": "Online", "Version": "PolycomVVX-VVX_150-UA/6.2.0.3937_64167f39299c",
        #      "Access Device External Id": ""},
        # ]}}

        # log.write(self.parse_response(devices_response, level))
        devices = devices_response['data']['accessDeviceTable']

        matched_devices = list()
        if not device_types:
            matched_devices = deepcopy(devices)
        else:
            for device in devices:
                device_type = device['Device Type']
                if device_type in device_types:
                    matched_devices.append(device)

        devices_info = dict()
        for device in matched_devices:
            device_name = device['Device Name']
            device_type = device['Device Type']
            log.write('    {}Device {}::{}::{})\n'.format(
                '    ' * (level + 1),
                self._process.parameters['provider_id'],
                self._process.parameters['group_id'],
                device_name)
            )
            log.write('    {}GroupAccessDeviceGetUserListRequest({}, {}, {}) '.format(
                '    ' * (level + 2),
                self._process.parameters['provider_id'],
                self._process.parameters['group_id'],
                device_name)
            )
            # users_response = {"data": {"deviceUserTable": [
            #     {"Line/Port": "ipvevvx400@telapexinc.com", "Last Name": "vvx",
            #      "First Name": "test", "Phone Number": "", "User Id": "ipvevvx400@telapexinc.com",
            #      "User Type": "Normal", "Endpoint Type": "Primary", "Order": 1,
            #      "Primary Line/Port": True, "Extension": 2589, "Department": "d1",
            #      "Email Address": "", "Private Identity": "", "Hotline Contact": ""}
            # ]}}
            users_response = self._bw.GroupAccessDeviceGetUserListRequest(
                self._process.parameters['provider_id'],
                self._process.parameters['group_id'], device_name
            )
            log.write(self.parse_response(users_response, level))
            users = users_response['data']['deviceUserTable']
            devices_info[device_type] = {
                "device_name": device_name, "mac_address": device["MAC Address"], "users": users
            }
        for device_type, device_info in devices_info.items():
            if self._process.parameters['department'] is None:
                devices_info[device_type]["matched_users"] = deepcopy(device_info["users"])
            else:
                matched_users = list()
                for user in device_info["users"]:
                    if user["Department"] == self._process.parameters['department']:
                        matched_users.append(user)
                devices_info[device_type]["matched_users"] = deepcopy(matched_users)
        result = list()

        for device_type, device_info in devices_info.items():
            for user in device_info["matched_users"]:
                result.append({"provider_id": self._process.parameters['provider_id'],
                               "group_id": self._process.parameters['group_id'],
                               "device_type": device_type, "mac_address": device_info["mac_address"],
                               "department": user["Department"], "user_id": user["User Id"],
                               "line_port": user["Line/Port"]})
        return {'log': log.getvalue(), 'summary': summary.getvalue(), "result": result}

    # def get_arbitary_result(self):
    #     result = list()
    #
    #     for _ in range(10):
    #         result.append({"provider_id": self._process.parameters['provider_id'],
    #                        "group_id": self._process.parameters['group_id'],
    #                        "device_type": 'Device Type A', "mac_address": 'Some MAC Address',
    #                        "department": 'Department A', "user_id": '1',
    #                        "line_port": _})
    #     return result

def swap_device(self, provider_id, group_id, device_name, device_type, **kwargs):
        log = io.StringIO()
        summary = io.StringIO()
        level = kwargs.get('level', 0)
        log.write('{}Migrate Polycom Generic: {}::{}::{} ({})\n'.format('    '*level, provider_id, group_id, device_name, device_type))
        
        # Device Type & Info from P1 parameters
        
        # Current Device Info
        if provider_id and group_id and device_name:
            log.write('{}GroupAccessDeviceGetRequest18sp1({}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name))
            resp0 = self._bw.GroupAccessDeviceGetRequest18sp1(provider_id, group_id, device_name)
            log.write(self.parse_response(resp0, level))
            device_info = resp0['data']
        elif provider_id and device_name:
            log.write('{}ServiceProviderAccessDeviceGetRequest18sp1({}, {}) '.format('    '*(level+1), provider_id, device_name))
            resp1 = self._bw.ServiceProviderAccessDeviceGetRequest18sp1(provider_id, device_name)
            log.write(self.parse_response(resp1, level))
            device_info = resp1['data']
        else:
            log.write('{}Could not determine device type for {}:{}:{}, not enough data\n'.format('    '*(level+1), provider_id, group_id, device_name))
            summary.write('"{}","{}","{}","{}","{}","{}","{}"\n'.format(provider_id, group_id, device_type, device_name, '', '', 'Could not retrieve device details'))
            return {'log': log.getvalue(), 'summary': summary.getvalue()}

        # New device info
        device_name_2 = '{}_{}'.format(device_name, device_suffix)
        device_username_2 = device_info['userName']
        device_password_2 = '8675309'

        # Build Configuration Files
        redirect_file_contents = '<change device.set="1" device.dhcp.bootSrvUseOpt.set="1" device.dhcp.bootSrvUseOpt="Static" device.prov.user.set="1" device.prov.user="{username}" device.prov.password.set="1" device.prov.password="{password}" device.prov.serverType.set="1" device.prov.serverType="HTTP" device.prov.serverName.set="1" device.prov.serverName="bwdms.cspirefiber.com/dms/PolycomVVX" />'.format(username=device_username_2, password=device_password_2)
        custom_redirect_file_base64 = base64.b64encode(redirect_file_contents.encode('utf-8')).decode('utf-8')


        # Set existing device's primary line/port (if necessary)
        if 'line_ports' in kwargs:
            line_ports = kwargs['line_ports']
        else:
            log.write('{}GroupAccessDeviceGetUserListRequest({}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name))
            resp0 = self._bw.GroupAccessDeviceGetUserListRequest(provider_id, group_id, device_name)
            log.write(self.parse_response(resp0, level))
            line_ports = sorted(resp0['data']['deviceUserTable'], key=lambda k: k['Order'])
        if len(line_ports) > 0 and not BroadWorksDeviceMigration.has_primary_line_port(line_ports):
            line_port = BroadWorksDeviceMigration.get_first_primary_line_port(line_ports)
            if line_port is not None:
                log.write('{}GroupAccessDeviceModifyUserRequest({}, {}, {}, {}, isPrimaryLinePort={}) '.format('    '*(level+1), provider_id, group_id, device_name, line_port['Line/Port'], True))
                resp1 = self._bw.GroupAccessDeviceModifyUserRequest(serviceProviderId=provider_id, groupId=group_id, deviceName=device_name, linePort=line_port['Line/Port'], isPrimaryLinePort=True)
                log.write(self.parse_response(resp1, level))

        # Create new device
        log.write('{}GroupAccessDeviceAddRequest14({}, {}, {}, {}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name_2, device_type_2, device_username_2, device_password_2))
        resp1 = self._bw.GroupAccessDeviceAddRequest14(provider_id, group_id, device_name_2, device_type_2, username=device_username_2, password=device_password_2)
        log.write(self.parse_response(resp1, level))
        if resp1['type'] == 'c:ErrorResponse':
            # could not build device, ruh roh!
            summary.write('"{}","{}","{}","{}","{}","{}","{}"\n'.format(provider_id, group_id, device_type, device_name, device_type_2, device_name_2, 'ERROR: Could not add new device'))
            return {'log': log.getvalue(), 'summary': summary.getvalue()}

        # Move device tags to new device
        log.write('{}GroupAccessDeviceCustomTagGetListRequest({}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name))
        resp2 = self._bw.GroupAccessDeviceCustomTagGetListRequest(provider_id, group_id, device_name)
        log.write(self.parse_response(resp2, level))
        device_tags = resp2['data']['deviceCustomTagsTable']
        for tag in device_tags:
            if tag['Tag Name'] not in ['%APP_VERSION%', '%APP_VERSION_VVX-400%', '%APP_VERSION_VVX-500%', '%APP_VERSION_VVX-600%']:
                log.write('{}GroupAccessDeviceCustomTagAddRequest({}, {}, {}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name_2, tag['Tag Name'], tag['Tag Value']))
                resp3 = self._bw.GroupAccessDeviceCustomTagAddRequest(provider_id, group_id, device_name_2, tag['Tag Name'], tag['Tag Value'])
                log.write(self.parse_response(resp3, level))

        # Send existing device a new config file to redirect to the new device provisioning url + credentials
        log.write('{}GroupAccessDeviceFileModifyRequest14sp8({}, {}, {}, {}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name, 'phone%BWDEVICEID%.cfg', 'Custom', '{...}'))
        resp4 = self._bw.GroupAccessDeviceFileModifyRequest14sp8(serviceProviderId=provider_id, groupId=group_id, deviceName=device_name, fileFormat='phone%BWDEVICEID%.cfg', fileSource='Custom', uploadFile={'fileContent': custom_redirect_file_base64})
        log.write(self.parse_response(resp4, level))
        log.write('{}GroupCPEConfigRebuildDeviceConfigFileRequest({}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name))
        resp5 = self._bw.GroupCPEConfigRebuildDeviceConfigFileRequest(serviceProviderId=provider_id, groupId=group_id, deviceName=device_name)
        log.write(self.parse_response(resp5, level))
        log.write('{}GroupAccessDeviceResetRequest({}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name))
        resp6 = self._bw.GroupAccessDeviceResetRequest(serviceProviderId=provider_id, groupId=group_id, deviceName=device_name)
        log.write(self.parse_response(resp6, level))

        # Move line/ports from old to new device
        for line_port in line_ports:
            if line_port['Endpoint Type'] == 'Primary':
                # Remove Primary Line/Port from previous device
                log.write('{}UserModifyRequest17sp4({}, endpoint={}) '.format('    '*(level+1), line_port['User Id'], 'Nil()'))
                resp7 = self._bw.UserModifyRequest17sp4(userId=line_port['User Id'], endpoint=Nil())
                log.write(self.parse_response(resp7, level))
                # Add Primary Line/Port to new device
                access_device_endpoint = OrderedDict()
                access_device_endpoint['accessDevice'] = OrderedDict()
                access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
                access_device_endpoint['accessDevice']['deviceName'] = device_name_2
                access_device_endpoint['linePort'] = line_port['Line/Port']
                log.write('{}UserModifyRequest17sp4({}, endpoint={}) '.format('    '*(level+1), line_port['User Id'], '{...}'))
                resp8 = self._bw.UserModifyRequest17sp4(userId=line_port['User Id'], endpoint={'accessDeviceEndpoint': access_device_endpoint})
                log.write(self.parse_response(resp8, level))
            elif line_port['Endpoint Type'] == 'Shared Call Appearance':
                # Remove SCA from previous device
                access_device_endpoint = OrderedDict()
                access_device_endpoint['accessDevice'] = OrderedDict()
                access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
                access_device_endpoint['accessDevice']['deviceName'] = device_name
                access_device_endpoint['linePort'] = line_port['Line/Port']
                log.write('{}UserSharedCallAppearanceDeleteEndpointListRequest14({}, {}) '.format('    '*(level+1), line_port['User Id'], '{...}'))
                resp9 = self._bw.UserSharedCallAppearanceDeleteEndpointListRequest14(line_port['User Id'], access_device_endpoint)
                log.write(self.parse_response(resp9, level))
                # Add SCA to new device
                access_device_endpoint = OrderedDict()
                access_device_endpoint['accessDevice'] = OrderedDict()
                access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
                access_device_endpoint['accessDevice']['deviceName'] = device_name_2
                access_device_endpoint['linePort'] = line_port['Line/Port']
                log.write('{}UserSharedCallAppearanceAddEndpointRequest14sp2({}, {}, isActive=True, allowOrigination=True, allowTermination=True) '.format('    '*(level+1), line_port['User Id'], '{...}'))
                resp10 = self._bw.UserSharedCallAppearanceAddEndpointRequest14sp2(line_port['User Id'], access_device_endpoint, isActive=True, allowOrigination=True, allowTermination=True)
                log.write(self.parse_response(resp10, level))
            else:
                log.write('unknown line_port endpoint type :-(\n')

        # Set new device's primary line/port (if necessary)
        log.write('{}GroupAccessDeviceGetUserListRequest({}, {}, {}) '.format('    '*(level+1), provider_id, group_id, device_name_2))
        resp11 = self._bw.GroupAccessDeviceGetUserListRequest(provider_id, group_id, device_name_2)
        log.write(self.parse_response(resp11, level))
        line_ports = sorted(resp11['data']['deviceUserTable'], key=lambda k: k['Order'])
        if len(line_ports) > 0 and not BroadWorksDeviceMigration.has_primary_line_port(line_ports):
            line_port = BroadWorksDeviceMigration.get_first_primary_line_port(line_ports)
            if line_port is not None:
                log.write('{}GroupAccessDeviceModifyUserRequest({}, {}, {}, {}, isPrimaryLinePort=True) '.format('    '*(level+1), provider_id, group_id, device_name_2, line_port['Line/Port']))
                resp11 = self._bw.GroupAccessDeviceModifyUserRequest(serviceProviderId=provider_id, groupId=group_id, deviceName=device_name_2, linePort=line_port['Line/Port'], isPrimaryLinePort=True)
                log.write(self.parse_response(resp11, level))

        # Success!
        log.write('{}Migrated Device {}::{}::{} with UserAgent of {}\n'.format('    '*(level+1), provider_id, group_id, device_name, device_info['version']))
        summary.write('"{}","{}","{}","{}","{}","{}","{}"\n'.format(provider_id, group_id, device_type, device_name, device_type_2, device_name_2, "Success"))
        return {'log': log.getvalue(), 'summary': summary.getvalue()}


def filter_device_swap(process_id):
    process = Process.objects.get(id=process_id)

    # Summary Tab
    summary_content = ProcessContent.objects.create(process=process, tab='Summary', priority=1)
    dir_path = os.path.join(settings.PROTECTED_ROOT, 'process')
    filename_html = '{}_{}'.format(process.id, 'summary.html')
    pathname_html = os.path.join(dir_path, filename_html)
    filename_raw = '{}_{}'.format(process.id, 'summary.csv')
    pathname_raw = os.path.join(dir_path, filename_raw)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    summary_html = open(pathname_html, "w")
    summary_content.html.name = os.path.join('process', filename_html)
    summary_raw = open(pathname_raw, "w")
    summary_content.raw.name = os.path.join('process', filename_raw)
    summary_content.save()

    # Log Tab
    log_content = ProcessContent.objects.create(process=process, tab='Log', priority=2)
    dir_path = os.path.join(settings.PROTECTED_ROOT, 'process')
    filename_raw = '{}_{}'.format(process.id, 'log.txt')
    pathname_raw = os.path.join(dir_path, filename_raw)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    log_raw = open(pathname_raw, "w")
    log_content.raw.name = os.path.join('process', filename_raw)
    log_content.save()

    content = []

    try:
        print("Process {}: {} -> {}".format(process_id, process.method, process.parameters))
        process.status = process.STATUS_RUNNING
        process.save(update_fields=['status'])

        ds = BroadWorkDeviceSwap(process=process)
        content = ds.device_swap_filter()["result"]

        # Initial content
        summary_html.write('<table class="table table-striped table-bordered table-hover">\n')
        summary_html.write('<tr>\n')
        summary_html.write(
            '\t<th>Provider Id</th><th>Group Id</th><th>Device A Type</th><th>Device A Id</th><th>Device B Type'
            '</th><th>Device B Id</th><th>Status</th>\n')
        summary_html.write('</tr>\n')
        summary_html.write('<tbody>\n')
        summary_raw.write(
            '"Provider Id","Group Id","Device A Type","Device A Id","Device B Type","Device B Id","Status"\n')

        # here will be updated due to new logic.

        # after things are finished
        # end html
        summary_html.write('</tbody>\n')
        summary_html.write('</table>\n')
        # save data
        process.status = process.STATUS_RUNNING
        # process.end_timestamp = timezone.now()
        # process.save(update_fields=['status', 'end_timestamp'])
        process.save(update_fields=['status'])
        # ds.logout()
    except Exception:
        process.status = process.STATUS_ERROR
        process.end_timestamp = timezone.now()
        process.exception = traceback.format_exc()
        process.save(update_fields=['status', 'exception', 'end_timestamp'])

    # Cleanup
    log_raw.close()
    summary_raw.close()
    summary_html.close()

    return content
