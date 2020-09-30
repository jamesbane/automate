#Python
import os
import io
import certifi
import pycurl

from datetime import datetime
from urllib.parse import urlencode
from zipfile import ZipFile
from lxml import etree
from sansayvcm_client.models import RouteTableLog, SansayVcmServer

class VcmClient:

    def __init__(self, client_id):
        server = SansayVcmServer.objects.get(client_id__exact=client_id)

        #need to check here if server doesnt exist or there are more than 1
        self._baseUrl = server.uri
        self._action = 'update'
        self._element = 'route' 

    def _logVcmRequest(self, req, resp):
        now = datetime.now()
        xml = req.get('xmlcfg')
        cluster = req.get('cluster_id')
        number = req.get('number')
        action = req.get('action')
        status = resp.get('status')

        log = RouteTableLog(cluster_id=cluster, number=number, action=action, xmlcfg=xml, result_status=status, created=now)
        log.save()
        return

    def _getVcmUrl(self, cluster):
        url = self._baseUrl + "/ROME/webresources/hrs/" + self._action + "/VSXi_" + self._element + "?clusterID=" + cluster
        return url

    def buildArchive(self, configs):
        archive = io.BytesIO()
        with ZipFile(archive, 'w') as zip_archive:
            for config in configs:
                xmlcfg = etree.fromstring(config.xmlcfg)
                filename = 'file-' + str(config.id) + '.xml'
                zip_archive.writestr(filename, str(etree.tostring(xmlcfg), 'utf-8'))

        return archive

    def _buildCurlReq(self, url):
        crl = pycurl.Curl()
        crl.setopt(crl.URL, url)
        crl.setopt(crl.USERPWD, '%s:%s' %('dev301solutions', 'jL6WP6UP4RjdKn3F'))
        crl.setopt(crl.CAINFO, certifi.where())
        #crl.setopt(pycurl.VERBOSE, True)
    
        return crl

    def _pushClusterConfig(self, cluster):
        url = self._baseUrl + "/ROME/webresources/hrs/pushVSXiClusterConfig?clusterID=" + cluster + "&sbcIDs=2"
        buffer = io.BytesIO()

        postData = {'clusterID': cluster, 'sbcIDs': '2'}

        psh = pycurl.Curl()
        psh.setopt(psh.URL, url)
        psh.setopt(psh.USERPWD, '%s:%s' %('superuser', 'sansay'))
        psh.setopt(psh.CAINFO, certifi.where())
        #psh.setopt(pycurl.VERBOSE, True)
        psh.setopt(psh.POSTFIELDS, urlencode(postData))
        psh.setopt(pycurl.WRITEDATA, buffer)
        
        psh.perform()
        status = psh.getinfo(psh.RESPONSE_CODE)
        psh.close()

        body = buffer.getvalue()
        return status

    def send(self, cluster, action, cfg):
        self._action = action
        url = self._getVcmUrl(cluster)

        crl = self._buildCurlReq(url)
        crl.setopt(crl.HTTPPOST, [
            ('fileupload', (
                crl.FORM_BUFFER, 'config.zip',
                crl.FORM_BUFFERPTR, cfg.getvalue(),
                #crl.FORM_FILE, 'config.zip', #use this for physical file upload vs from buffer
            )),
        ])

        # if delete, set HTTP req type to DELETE
        if self._action == 'delete':
            crl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

        crl.perform()
        status = crl.getinfo(crl.RESPONSE_CODE)
        crl.close()

        self._pushClusterConfig(cluster)

        # Log the request/response
        with ZipFile(cfg) as z:
            files = z.namelist()
            for name in files:
                with z.open(name) as f:
                    xmlstr = f.read().decode("utf-8")
                    xmlobj = etree.fromstring(xmlstr)
                    number = xmlobj.find('./XBRoute/digitMatch').text

                req = {"cluster_id": cluster, "number": number, "action": self._action, "xmlcfg": xmlstr }
                resp = {"status": status}
                self._logVcmRequest(req, resp)

        return status
