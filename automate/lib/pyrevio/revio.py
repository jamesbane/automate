#Python
import json
import requests
import ssl

from requests import adapters
from urllib3 import poolmanager

class TLSAdapter(adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx)


class RevClient:

    def __init__(self):
        self.baseUrl = 'https://restapi.rev.io/v1'

    def getInventoryItem(self, number):
        url = self.baseUrl + '/InventoryItem?search.identifier=' + number + '&search.inventory_type_id=1'
        headers = {"accept": "application/json"}
        #response = requests.request("GET", url, headers=headers, verify=False)
        response = requests.get(url, verify = False)

        data = json.loads(response.text)
        print(data)

        return

    def getInventoryItemNew(self, number):
        url = self.baseUrl + '/InventoryItem?search.identifier=' + number + '&search.inventory_type_id=1'

        session = requests.session()
        session.mount('https://', TLSAdapter())
        response = session.get(url)

        data = json.loads(response.text)
        print(data)

        return
