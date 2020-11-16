from sansayvcm_client.models import VcmRouteQueue
from sansayvcm_client.vcmclient import VcmClient
from automate.celery import app
#from celery.utils.log import get_task_logger
#logger = get_task_logger(__name__)

@app.task(name='run_vcm_queue')
def run_vcm_queue(client_id):
    rows = VcmRouteQueue.objects.filter(uuid__exact=client_id, status__exact='pending')
    
    if rows.count() > 0:
        vcm = VcmClient(client_id)
        archive = vcm.buildArchive(rows)

        returnStatus = vcm.send('2', 'update', archive)

        for routequeue in rows:
            if returnStatus == 200:
                routequeue.status = 'success'
            else:
                routequeue.status = 'error'

            routequeue.save()
    else:
        print('No queue items found')

        
