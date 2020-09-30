import os
import json
from lxml import etree
from datetime import datetime

#django
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.contrib.staticfiles.templatetags.staticfiles import static
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler

#Automate
import sansayvcm_client.forms
from sansayvcm_client.vcmclient import VcmClient
from sansayvcm_client.models import RouteTableLog, VcmRouteQueue
from sansayvcm_client.serializers import VcmRouteSerializer, VcmRouteMetadataSerializer

class IndexView(TemplateView):
    template_name = 'sansayvcm_client/index.html'

class SansayVcmRequestView(FormView):
    template_name = 'sansayvcm_client/modify_route_table.html'
    form_class = sansayvcm_client.forms.ModifyRouteTableForm 
    success_url = '/sansay-vcm-request'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            post = request.POST

            cluster = post.get('cluster')
            desc = post.get('alias')
            did = post.get('did')

            client = VcmClient('update', 'route')
            result = client.send(cluster, desc, did)

            return HttpResponseRedirect('/sansay/sansay-vcm-request')

class VcmLogView(ListView):
    model = RouteTableLog
    paginate_by = 25
    javascript = static('sansayvcm_client/routetablelog_list.js')

class VcmRouteQueueView(ListView):
    model = VcmRouteQueue
    paginate_by = 25


class VcmRoutes(APIView):

    def post(self, request, **kwargs):
        data = json.loads(request.body.decode("utf-8"))
        created = data['created_date'] if data['created_date'] != None else datetime.now()

        # Validate the data['metadata'] object
        serialized = VcmRouteMetadataSerializer(data=data['metadata'])
        if serialized.is_valid():
            data = serialized.validated_data
        else:
            return Response(
                {
                    'status': 'Errors found',
                    'errors': serialized.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        number = data['identifier']
        # normalize the number to 10 digit
        #if '+1' in number:
        #    number = number.replace('+1', '')

        alias = 'Cust ' + str(data['customer_id']) + ' ' + number
        
        xmlCfg = etree.parse(os.path.abspath('sansayvcm_client/configs/route.xml'))
        for field in xmlCfg.iter():
            if field.tag == 'alias':
                field.text = alias
            if field.tag == 'digitMatch':
                field.text = number

        queue = VcmRouteQueue(
            uuid=kwargs['uuid'],
            number=number,
            alias=alias,
            action=data['status'],
            create_date=created, 
            xmlcfg=str(etree.tostring(xmlCfg), 'utf-8'), 
            status='pending'
        )
        queue.save()

        return Response({'status': 'Created'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        return Response(None, status=status.HTTP_404_NOT_FOUND)
