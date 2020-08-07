#Python
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

    def _getConfigFile(self):
        xmlCfg = etree.parse('configs/route.xml')
        for field in xmlCfg.iter():
            #alias.attrib['value'] = 'Test Cust 12345 5858675309'
            if field.tag == 'alias':
                field.text = 'Test Cust 12345 5858675309'
            if field.tag == 'digitMatch':
                field.text = '5858675309'

        print(etree.tostring(xmlCfg, pretty_print=True))


x = VcmClient('update', 'route')
x._getConfigFile()

