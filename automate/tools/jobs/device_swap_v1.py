# Python
import base64
import io
import os
import re
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


class BroadWorkDeviceSwapFilter:
    _bw = None
    _content = io.StringIO()

    def __init__(self, process):
        self._process = process

        platform = self._process.platform_id
        self._bw = BroadWorks(url=platform.uri,
                              username=platform.username,
                              password=platform.password,
                              location=self._process.platform.uri)
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

    @staticmethod
    def has_primary_line_port(device_user_table):
        for line_port in device_user_table:
            if line_port['Primary Line/Port'] == 'true':
                return True
        return False

    @staticmethod
    def get_first_primary_line_port(line_ports):
        for line_port in line_ports:
            if line_port['Endpoint Type'] == 'Primary':
                return line_port
        return None

    # def device_swap_filter(self, group_id, input_device_types, department=None, provider_id=1003, **kwargs):
    def device_swap_filter(self, **kwargs):
        log = io.StringIO()
        summary = io.StringIO()
        level = kwargs.get('level', 0)
        input_device_types = self._process.parameters.get("input_device_types", [])
        log.write("{}Device Swap {}::{}::{}::{}\n".format(
            '    ' * level,
            self._process.parameters['provider_id'],
            self._process.parameters['group_id'],
            self._process.parameters['department'],
            input_device_types)
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

        # FIXME
        # log.write(self.parse_response(devices_response, level))

        devices = devices_response['data']['accessDeviceTable']
        matched_devices = list()
        if not input_device_types:
            matched_devices = deepcopy(devices)
        else:
            for device in devices:
                device_type = device['Device Type']
                if device_type in input_device_types:
                    matched_devices.append(device)

        for device in devices:
            parsed_version = BroadWorkDeviceSwapFilter.parse_version(device['Version'])
            device['Device Type'] = parsed_version['device_type'] or device['Device Type']
            device['MAC Address'] = parsed_version['mac_address'] or device['MAC Address']

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

            # FIXME
            # log.write(self.parse_response(users_response, level))

            users = users_response['data']['deviceUserTable']

            devices_info[device_type] = devices_info.get(device_type, list())
            devices_info[device_type].append(
                {"device_name": device_name,
                 "mac_address": device["MAC Address"],
                 "users": users}
            )

        for device_type, device_info_list in devices_info.items():
            for device_info in device_info_list:
                if self._process.parameters['department'] is None and self._process.parameters != '':
                    device_info["matched_users"] = deepcopy(device_info["users"])
                else:
                    matched_users = list()
                    for user in device_info["users"]:
                        if user["Department"] == self._process.parameters['department'] or self._process.parameters[
                            'department'] == '':
                            matched_users.append(user)
                    device_info["matched_users"] = deepcopy(matched_users)

        result = list()
        for device_type, device_info_list in devices_info.items():
            for device_info in device_info_list:
                for user in device_info["matched_users"]:
                    result.append({"provider_id": self._process.parameters['provider_id'],
                                   "group_id": self._process.parameters['group_id'],
                                   "device_type": device_type, "mac_address": device_info["mac_address"],
                                   "department": user["Department"], "user_id": user["User Id"],
                                   "device_name": device_info["device_name"],
                                   "line_port": user["Line/Port"]})
        print(result)
        return {'log': log.getvalue(), 'summary': summary.getvalue(), "result": result}

    @staticmethod
    def parse_version(version):
        """
        # currently supports Polycom devices only

        example version 'PolycomVVX-VVX_400-UA/5.9.5.0614_0004f28e5a79'
        """

        device_type, mac_address = ('',) * 2
        if version is None:
            return locals()

        if not version.lower().startswith('polycom'):
            return locals()

        try:
            parts = version.split('/')
            if len(parts) > 2:
                del parts[0]
            mac_address = re.findall(r'[0-9a-fA-F]{12}', parts[1])[0]
            device_type = re.findall(r'(?i)Polycom.*', parts[0])[0]
            if device_type.endswith('-UA'):
                device_type = device_type.replace('-UA', '')
        except (IndexError, ValueError):
            pass
        return locals()

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


def filter_device_swap(process_id):
    process = Process.objects.get(id=process_id)


    content = []

    try:
        print("Process {}: {} -> {}".format(process_id, process.method, process.parameters))
        process.status = process.STATUS_RUNNING
        process.save(update_fields=['status'])

        ds = BroadWorkDeviceSwapFilter(process=process)
        content = ds.device_swap_filter()["result"]
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

    return content
