from django.core.management.base import BaseCommand, CommandError
from sansayvcm_client.models import VcmRouteQueue
from sansayvcm_client.vcmclient import VcmClient

class Command(BaseCommand):
    help = 'Runs the route queue, processing rows that are pending.'

    def add_arguments(self, parser):
        parser.add_argument('client_id', nargs='+', type=int)

    def handle(self, *args, **options):
        try:
            rows = VcmRouteQueue.objects.filter(uuid__exact=options['client_id'][0])
        except VcmRouteQueue.DoesNotExist:
            raise CommandError('No queue entries found for client ID "%s"' % options['client_id'][0])

        vcm = VcmClient()
        archive = vcm.buildArchive(rows)
        print(archive)

        #for row in rows:
        #    print(row.xmlcfg)
        