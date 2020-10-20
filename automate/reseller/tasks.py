import datetime
import logging

from automate.celery import app
from lib.netsapiens.netsapiens import Netsapiens
from reseller.models import ResellerCount


@app.task(name='reseller_count')
def reseller_count():
    logging.debug("asdfadsf")
    now = datetime.datetime.now()
    netsapi = Netsapiens()
    resellers = netsapi.reseller_read()
    if resellers is not None:
        for item in resellers:
            reseller = ResellerCount()
            reseller.territory_id = item['territory_id']
            reseller.territory_name = item['territory']
            reseller.count_external = item['countExternal']
            reseller.count_for_limit = item['countForLimit']
            reseller.created_at = now

            print("add reseller")
            reseller.save()
