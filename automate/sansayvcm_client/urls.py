from django.urls import re_path

# Application
import sansayvcm_client.views

app_name ='sansayvcm_client'
urlpatterns = [
    re_path(r'^$', sansayvcm_client.views.IndexView.as_view(), name='index'),
    # Sansay VCM
    re_path(r'^sansay-vcm-request$', sansayvcm_client.views.SansayVcmRequestView.as_view(), name='sansay-vcm-request'),
    re_path(r'^vcm-route-log$', sansayvcm_client.views.VcmLogView.as_view(), name='vcm-route-logs'),
    re_path(r'^route-queue$', sansayvcm_client.views.VcmRouteQueueView.as_view(), name='route-queue'),
    re_path(r'^api/(?P<uuid>\d+)/route$', sansayvcm_client.views.VcmRoutes.as_view(), name='vcm-routes'),
]

