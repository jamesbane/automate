#django
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

#Automate
import sansayvcm_client.forms
from lib.pyutil.django.mixins import ProcessFormMixin

class IndexView(TemplateView):
    template_name = 'sansayvcm_client/index.html'

class SansayVcmRequestView(ProcessFormMixin, TemplateView):
    template_name = 'sansayvcm_client/modify_route_table.html'
    form_class = sansayvcm_client.forms.ModifyRouteTableForm 
