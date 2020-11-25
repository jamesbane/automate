#Python
import json
import requests
import ssl

from requests import adapters
from urllib3 import poolmanager
from django.conf import settings

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
        self.uname = '301solutions_sandbox@impulse_sandbox'
        self.pword = 'NePJRUHBJioWKzr9EJ6PwwXEvJNB^B6jCqNTJM,qqCs7JQyb7(YDb'

    def getInventoryItem(self, number):
        url = self.baseUrl + '/InventoryItem?search.identifier=' + number + '&search.inventory_type_id=1'

        session = requests.session()
        session.mount('https://', TLSAdapter())
        response = session.get(url, auth=(self.uname, self.pword))

        inventoryItem = json.loads(response.text)

        return inventoryItem

    def getCustomerProfile(self, custId):
        url = self.baseUrl + '/Customers/' + str(custId)

        session = requests.session()
        session.mount('https://', TLSAdapter())
        response = session.get(url, auth=(self.uname, self.pword))

        customer = json.loads(response.text)

        return customer
