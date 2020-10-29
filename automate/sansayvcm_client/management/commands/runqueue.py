from django.core.management.base import BaseCommand, CommandError
from sansayvcm_client.models import VcmRouteQueue
from sansayvcm_client.vcmclient import VcmClient

from zipfile import ZipFile
from lxml import etree

class Command(BaseCommand):
    help = 'Runs the route queue, processing rows that are pending.'

    def add_arguments(self, parser):
        parser.add_argument('client_id', nargs='+', type=int)

    def handle(self, *args, **options):
        client_id = options['client_id'][0]
        try:
            rows = VcmRouteQueue.objects.filter(uuid__exact=client_id, status__exact='pending')
        except VcmRouteQueue.DoesNotExist:
            raise CommandError('No queue entries found for client ID "%s"' % client_id)
        
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

        