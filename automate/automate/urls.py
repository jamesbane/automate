from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
import django.views.static
from django.conf.urls.static import static

import api.urls
import automate.views

# no 1. removed namespace='auth' from  re_path(r'^accounts/', include('django.contrib.auth.urls', )),
#because of no 1. above you need to do no 2. below after installing a new django
#no 2. put   app_name = 'auth' inside django.contrib.auth.urls file. 
#  you can find it inside the  (Lib\site-packages\django\contrib\auth\urls.py)
urlpatterns = [
  re_path(r'^$', automate.views.IndexRedirectView.as_view(), name='index'),

    re_path(r'^accounts/', include('django.contrib.auth.urls',  )),
    re_path(r'^dashboard/', include('dashboard.urls', ),name='dashboard-url'),
    re_path(r'^deploy/', include('deploy.urls', )),
    re_path(r'^django-rq/', include('django_rq.urls')),
    re_path(r'^dms/', include('dms.urls', )),
    re_path(r'^routing/', include('routing.urls', )),
    re_path(r'^tools/', include('tools.urls',),name='tools-url'),
    re_path(r'^reseller/', include('reseller.urls',), name='reseller-url'),
    re_path(r'^protected/(?P<path>.*)$', automate.views.ProtectedFileView.as_view()),
    re_path(r'^sansay/', include('sansayvcm_client.urls',)),

    # Django Rest Framework
    re_path(r'^api/', include(api.urls, )),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Django admin
   re_path(r'^admin/', admin.site.urls),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Allow serving media content if in debug mode
urlpatterns += [
   re_path(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT,}),
]
    
