import os
import json
from lxml import etree

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

#Automate
import sansayvcm_client.forms
from sansayvcm_client.vcmclient import VcmClient
from sansayvcm_client.models import RouteTableLog, VcmRouteQueue

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
    paginate_by = 100
    javascript = static('sansayvcm_client/routetablelog_list.js')

class VcmRoutes(APIView):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        
        xmlCfg = etree.parse(os.path.abspath('sansayvcm_client/configs/route.xml'))
        for field in xmlCfg.iter():
            if field.tag == 'alias':
                field.text = 'Customer: ' + str(data['metadata']['customer_id']) 
            if field.tag == 'digitMatch':
                field.text = data['metadata']['identifier']

        queue = VcmRouteQueue(uuid=1234, create_date=data['created_date'], xmlcfg=str(etree.tostring(xmlCfg), 'utf-8'), status='pending')
        queue.save()

        return Response(str(etree.tostring(xmlCfg), 'utf-8'))

