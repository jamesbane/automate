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
from lib.bw.util import Util


class BroadWorkDeviceSwapPh2:
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

    @staticmethod
    def parse_response(response, level):
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

    def device_swap(self, **kwargs):
        log = io.StringIO()
        summary = io.StringIO()
        level = kwargs.get('level', 0)
        provider_id = self._process.parameters['provider_id']
        group_id = self._process.parameters['group_id']
        devices_info = self._process.parameters.get("devices_info", [])
        new_device_type = self._process.parameters.get("new_device_type", [])
        log.write("{}Device Swap {}::{}::{}::{}\n".format(
            '    ' * level, provider_id, group_id, devices_info, new_device_type))

        for info in devices_info:
            current_device_type = info["device_type"]
            current_device_name = info["device_name"]
            current_mac_address = info["mac_address"]
            device_suffix = Util.random_password(length=6, specials=False)
            new_device_name = '{}_{}'.format(current_device_name, device_suffix)

            # Set existing device's primary line/port (if necessary)
            log.write('{}GroupAccessDeviceGetUserListRequest({}, {}, {}) '.format(
                '    ' * (level + 1), provider_id, group_id, current_device_name))
            resp0 = self._bw.GroupAccessDeviceGetUserListRequest(provider_id, group_id, current_device_name)
            log.write(BroadWorkDeviceSwapPh2.parse_response(resp0, level))
            line_ports = sorted(resp0["data"]["deviceUserTable"], key=lambda k: k["Order"])

            if len(line_ports) > 0 and not BroadWorkDeviceSwapPh2.has_primary_line_port(line_ports):
                line_port = BroadWorkDeviceSwapPh2.get_first_primary_line_port(line_ports)
                if line_port is not None:
                    log.write('{}GroupAccessDeviceModifyUserRequest({}, {}, {}, {}, isPrimaryLinePort={}) '.format(
                        '    ' * (level + 1), provider_id, group_id, current_device_name,
                        line_port['Line/Port'], True))
                    resp1 = self._bw.GroupAccessDeviceModifyUserRequest(serviceProviderId=provider_id,
                                                                        groupId=group_id,
                                                                        deviceName=current_device_name,
                                                                        linePort=line_port['Line/Port'],
                                                                        isPrimaryLinePort=True)
                    log.write(BroadWorkDeviceSwapPh2.parse_response(resp1, level))

            # Create new device
            log.write('{}GroupAccessDeviceAddRequest14({}, {}, {}, {}, {}) '.format(
                '    ' * (level + 1), provider_id, group_id, new_device_name,
                new_device_type, current_mac_address))
            resp1 = self._bw.GroupAccessDeviceAddRequest14(provider_id, group_id, new_device_name,
                                                           new_device_type,
                                                           macAddress=current_mac_address)
            log.write(BroadWorkDeviceSwapPh2.parse_response(resp1, level))
            if resp1['type'] == 'c:ErrorResponse':
                # could not build device!
                summary.write(
                    '"{}","{}","{}","{}","{}","{}","{}"\n'.format(
                        provider_id, group_id, current_device_type, current_device_name,
                        new_device_type, new_device_name, 'ERROR: Could not add new device'))
                return {'log': log.getvalue(), 'summary': summary.getvalue()}

            # Move device tags to new device
            log.write('{}GroupAccessDeviceCustomTagGetListRequest({}, {}, {}) '.format(
                '    ' * (level + 1), provider_id, group_id, current_device_name))
            resp2 = self._bw.GroupAccessDeviceCustomTagGetListRequest(provider_id, group_id, current_device_name)
            log.write(BroadWorkDeviceSwapPh2.parse_response(resp2, level))
            device_tags = resp2['data']['deviceCustomTagsTable']
            for tag in device_tags:
                log.write('{}GroupAccessDeviceCustomTagAddRequest({}, {}, {}, {}, {}) '.format(
                    '    ' * (level + 1), provider_id, group_id, new_device_name,
                    tag['Tag Name'], tag['Tag Value']))
                resp3 = self._bw.GroupAccessDeviceCustomTagAddRequest(provider_id, group_id, new_device_name,
                                                                      tag['Tag Name'], tag['Tag Value'])
                log.write(BroadWorkDeviceSwapPh2.parse_response(resp3, level))

            # Move line/ports from old to new device
            for line_port in line_ports:
                if line_port['Endpoint Type'] == 'Primary':

                    # Remove Primary Line/Port from previous device
                    log.write('{}UserModifyRequest17sp4({}, endpoint={}) '.format(
                        '    ' * (level + 1), line_port['User Id'], 'Nil()'))
                    resp7 = self._bw.UserModifyRequest17sp4(userId=line_port['User Id'], endpoint=Nil())
                    log.write(BroadWorkDeviceSwapPh2.parse_response(resp7, level))

                    # Add Primary Line/Port to new device
                    access_device_endpoint = OrderedDict()
                    access_device_endpoint['accessDevice'] = OrderedDict()
                    access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
                    access_device_endpoint['accessDevice']['deviceName'] = new_device_name
                    access_device_endpoint['linePort'] = line_port['Line/Port']
                    log.write('{}UserModifyRequest17sp4({}, endpoint={}) '.format(
                        '    ' * (level + 1), line_port['User Id'], '{...}'))
                    resp8 = self._bw.UserModifyRequest17sp4(userId=line_port['User Id'],
                                                            endpoint={'accessDeviceEndpoint': access_device_endpoint})
                    log.write(BroadWorkDeviceSwapPh2.parse_response(resp8, level))

                elif line_port['Endpoint Type'] == 'Shared Call Appearance':
                    # Remove SCA from previous device
                    access_device_endpoint = OrderedDict()
                    access_device_endpoint['accessDevice'] = OrderedDict()
                    access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
                    access_device_endpoint['accessDevice']['deviceName'] = current_device_name
                    access_device_endpoint['linePort'] = line_port['Line/Port']
                    log.write('{}UserSharedCallAppearanceDeleteEndpointListRequest14({}, {}) '.format(
                        '    ' * (level + 1), line_port['User Id'], '{...}'))
                    resp9 = self._bw.UserSharedCallAppearanceDeleteEndpointListRequest14(line_port['User Id'],
                                                                                         access_device_endpoint)
                    log.write(BroadWorkDeviceSwapPh2.parse_response(resp9, level))
                    # Add SCA to new device
                    access_device_endpoint = OrderedDict()
                    access_device_endpoint['accessDevice'] = OrderedDict()
                    access_device_endpoint['accessDevice']['deviceLevel'] = 'Group'
                    access_device_endpoint['accessDevice']['deviceName'] = new_device_name
                    access_device_endpoint['linePort'] = line_port['Line/Port']
                    log.write('{}UserSharedCallAppearanceAddEndpointRequest14sp2({}, {}, isActive=True,'
                              ' allowOrigination=True, allowTermination=True) '.format(
                        '    ' * (level + 1), line_port['User Id'], '{...}'))
                    resp10 = self._bw.UserSharedCallAppearanceAddEndpointRequest14sp2(line_port['User Id'],
                                                                                      access_device_endpoint,
                                                                                      isActive=True,
                                                                                      allowOrigination=True,
                                                                                      allowTermination=True)
                    log.write(BroadWorkDeviceSwapPh2.parse_response(resp10, level))
                else:
                    log.write('unknown line_port endpoint type :-(\n')

            # Set new device's primary line/port (if necessary)
            log.write('{}GroupAccessDeviceGetUserListRequest({}, {}, {}) '.format(
                '    ' * (level + 1), provider_id, group_id, new_device_name))
            resp11 = self._bw.GroupAccessDeviceGetUserListRequest(provider_id, group_id, new_device_name)
            log.write(BroadWorkDeviceSwapPh2.parse_response(resp11, level))
            line_ports = sorted(resp11['data']['deviceUserTable'], key=lambda k: k['Order'])

            if len(line_ports) > 0 and not BroadWorkDeviceSwapPh2.has_primary_line_port(line_ports):
                line_port = BroadWorkDeviceSwapPh2.get_first_primary_line_port(line_ports)
                if line_port is not None:
                    log.write('{}GroupAccessDeviceModifyUserRequest({}, {}, {}, {}, isPrimaryLinePort=True) '.format(
                        '    ' * (level + 1), provider_id, group_id, new_device_name, line_port['Line/Port']))
                    resp11 = self._bw.GroupAccessDeviceModifyUserRequest(serviceProviderId=provider_id,
                                                                         groupId=group_id,
                                                                         deviceName=new_device_name,
                                                                         linePort=line_port['Line/Port'],
                                                                         isPrimaryLinePort=True)
                    log.write(BroadWorkDeviceSwapPh2.parse_response(resp11, level))

            # Success!
            log.write('{}Swapped Device {}::{}::{} to {}\n'.format(
                '    ' * (level + 1), provider_id, group_id, current_device_name, new_device_type))
            summary.write('"{}","{}","{}","{}","{}","{}","{}"\n'.format(
                provider_id, group_id, current_device_type, current_device_name,
                new_device_type, new_device_name, "Success"))
        return {'log': log.getvalue(), 'summary': summary.getvalue()}


def device_swap_ph2(process_id):
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

        ds = BroadWorkDeviceSwapPh2(process=process)
        content = ds.device_swap()
        content = content["summary"]

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

        # after things are finished
        # end html
        summary_html.write('</tbody>\n')
        summary_html.write('</table>\n')
        # save data
        process.status = process.STATUS_COMPLETED
        process.end_timestamp = timezone.now()
        process.save(update_fields=['status', 'end_timestamp'])
        # ds.logout()
    except Exception as e:
        print("Exception")
        print(e)
        process.status = process.STATUS_ERROR
        process.end_timestamp = timezone.now()
        process.exception = traceback.format_exc()
        process.save(update_fields=['status', 'exception', 'end_timestamp'])

    # Cleanup
    log_raw.close()
    summary_raw.close()
    summary_html.close()

    return content
