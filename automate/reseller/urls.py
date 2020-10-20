from django.urls import re_path

from reseller.views import CallCountFormView

app_name = 'reseller'
urlpatterns = [
    re_path(r'^call-count$', CallCountFormView.as_view(), name='call-count'),
]
