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
from lib.pybw.broadworks import (BroadWorks, Nil)


class BroadWorkDeviceSwap:
    _bw = None
    _content = io.StringIO()

    def __init__(self, process, username, password):
        self._process = process

        platform = self._process.platform_id
        self._bw = BroadWorks(url=platform.uri,
                              username=username,
                              password=password)
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

    def device_swap(self, group_id, device_types, department=None, provider_id=1003, **kwargs):
        log = io.StringIO()
        summary = io.StringIO()
        level = kwargs.get('level', 0)
        log.write("{}Device Swap {}::{}::{}::{}\n".format('    ' * level, provider_id, group_id,
                                                          department, device_types))

        # get devices
        log.write('    {}Devices\n'.format('    ' * level))
        log.write('    {}GroupAccessDeviceGetListRequest({}, {}) '.format('    ' * (level + 1), provider_id, group_id))
        devices_response = self._bw.GroupAccessDeviceGetListRequest(provider_id, group_id)
        log.write(self.parse_response(devices_response, level))
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
            log.write('    {}Device {}::{}::{})\n'.format('    ' * (level + 1), provider_id, group_id, device_name))
            log.write('    {}GroupAccessDeviceGetUserListRequest({}, {}, {}) '.format('    ' * (level + 2), provider_id,
                                                                                      group_id, device_name))
            users_response = self._bw.GroupAccessDeviceGetUserListRequest(provider_id, group_id, device_name)
            log.write(self.parse_response(users_response, level))
            users = users_response['data']['deviceUserTable']
            devices_info[device_type] = {
                "device_name": device_name, "mac_address": device["MAC Address"], "users": users
            }

        for device_type, device_info in devices_info.items():
            if department is None:
                devices_info[device_type]["matched_users"] = deepcopy(device_info["users"])
            else:
                matched_users = list()
                for user in device_info["users"]:
                    if user["Department"] == department:
                        matched_users.append(user)
                devices_info[device_type]["matched_users"] = deepcopy(matched_users)

        result = list()

        for device_type, device_info in devices_info:
            for user in device_info["matched_users"]:
                result.append({"provider_id": provider_id, "group_id": group_id,
                               "device_type": device_type, "mac_address": device_info["mac_address"],
                               "department": user["Department"], "user_id": user["User Id"],
                               "line_port": user["Line/Port"]})

        return {'log': log.getvalue(), 'summary': summary.getvalue(), "result": result}

    @staticmethod
    def get_arbitary_result(group_id, device_types, department=None, provider_id=1003, **kwarg):
        result = list()

        for _ in range(10):
            result.append({"provider_id": provider_id, "group_id": group_id,
                           "device_type": 'Device Type A', "mac_address": 'Some MAC Address',
                           "department": 'Department A', "user_id": '1',
                           "line_port": _})
        return result

def device_swap(process_id):
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

    try:
        print("Process {}: {} -> {}".format(process_id, process.method, process.parameters))
        process.status = process.STATUS_RUNNING
        process.save(update_fields=['status'])

        ds = BroadWorkDeviceSwap(process=process)
        content = dict()

        # Retrieve Data
        provider_type = process.parameters.get('provider_type', None)
        provider_id = process.parameters.get('provider_id', None)
        group_id = process.parameters.get('group_id', None)

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
        process.status = process.STATUS_COMPLETED
        process.end_timestamp = timezone.now()
        process.save(update_fields=['status', 'end_timestamp'])
        ds.logout()
    except Exception:
        process.status = process.STATUS_ERROR
        process.end_timestamp = timezone.now()
        process.exception = traceback.format_exc()
        process.save(update_fields=['status', 'exception', 'end_timestamp'])

    # Cleanup
    log_raw.close()
    summary_raw.close()
    summary_html.close()
