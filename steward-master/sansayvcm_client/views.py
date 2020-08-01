#django
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

#Automate
import sansayvcm_client.forms

class IndexView(TemplateView):
    template_name = 'sansayvcm_client/index.html'

class SansayVcmRequestView(FormView):
    template_name = 'sansayvcm_client/modify_route_table.html'
    form_class = sansayvcm_client.forms.ModifyRouteTableForm 
    success_url = '/sansay-vcm-request'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            print(request.POST)
            return HttpResponseRedirect('/sansay/sansay-vcm-request')

