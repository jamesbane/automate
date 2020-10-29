import datetime

from automate.celery import app
from lib.netsapiens.netsapiens import Netsapiens
from reseller.models import ResellerCount, ResellerPlatform


@app.task(name='reseller_count')
def reseller_count():
    now = datetime.datetime.now()
    platforms = ResellerPlatform.objects.all()
    for platform in platforms:
        netsapi = Netsapiens(platform_id=platform.id)
        resellers = netsapi.reseller_read()
        if resellers is not None:
            for item in resellers:
                reseller = ResellerCount()
                reseller.customer = platform.customer
                reseller.territory_id = item['territory_id']
                reseller.territory_name = item['territory']
                reseller.count_external = item['countExternal']
                reseller.count_for_limit = item['countForLimit']
                reseller.created_at = now
                reseller.save()
