from django.urls import re_path

from reseller.views import CallCountFormView, ExportCSVFormView

app_name = 'reseller'
urlpatterns = [
    re_path(r'^call-count$', CallCountFormView.as_view(), name='call-count'),
    re_path(r'^export-csv$', ExportCSVFormView.as_view(), name='export-csv')
]
