#djano
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

#Automate
import sansayvcm_client.forms

class SansayVcmRequestView(PermissionRequiredMixin, LoginRequiredMixin):
    template_name = 'sansayvcm_client/modify_route_table.html'
    form_class = sansayvcm_client.forms.ModifyRouteTableForm. 
