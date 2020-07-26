#django
from django import forms

#local
from .models import SansayVcmServer, SansayCluster

class SansayVcmServerForm(forms.Form):
    server = forms.ModelChoiceField(label="Sansay Server", queryset=SansayVcmServer.objects.all())

class ModifyRouteTableForm(SansayVcmServerForm):
    cluster = forms.ModelChoiceField(label="Cluster", queryset=SansayCluster.objects.all())
