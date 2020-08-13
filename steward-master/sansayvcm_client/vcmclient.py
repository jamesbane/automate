#Python
import os
import io
import certifi
from urllib.parse import urlencode
from zipfile import ZipFile
from lxml import etree
import pycurl

class VcmClient:

    def __init__(self, action, element):
        self._baseUrl = 'https://labvcm.impulsevoip.net:8888'
        self._action = 'update'
        self._element = 'route' 
        
        if action in ['update', 'replace', 'delete', 'download']:
            self._action = action

        # Will there be other elements allowed?
        if element in ['route']:
            self._element = element

    def _getVcmUrl(self, cluster):
        url = self._baseUrl + "/ROME/webresources/hrs/" + self._action + "/VSXi_" + self._element + "?clusterID=" + cluster
        return url

    def _getConfigFile(self, desc, number):
        xmlCfg = etree.parse(os.path.abspath('sansayvcm_client/configs/route.xml'))
        for field in xmlCfg.iter():
            if field.tag == 'alias':
                field.text = desc
            if field.tag == 'digitMatch':
                field.text = number

        archive = io.BytesIO()
        with ZipFile(archive, 'w') as zip_archive:
            zip_archive.writestr('config.xml', str(etree.tostring(xmlCfg), 'utf-8'))

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
        print(body.decode('utf-8'))

        return status

    def send(self, cluster, desc, number):
        url = self._getVcmUrl(cluster)
        cfg = self._getConfigFile(desc, number)

        crl = self._buildCurlReq(url)
        crl.setopt(crl.HTTPPOST, [
            ('fileupload', (
                crl.FORM_BUFFER, 'config.zip',
                crl.FORM_BUFFERPTR, cfg.getvalue(),
                #crl.FORM_FILE, 'config.zip', #use this for physical file upload vs from buffer
            )),
        ])

        crl.perform()
        status = crl.getinfo(crl.RESPONSE_CODE)
        crl.close()

        self._pushClusterConfig(cluster)
        return status

x = VcmClient('update', 'route')
x.send('2', 'Test Client Dev301Solutions', '8058845678')
#x._pushClusterConfig('2')

