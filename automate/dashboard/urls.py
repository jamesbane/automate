from django.urls import path,re_path
import dashboard.views

app_name ='dashboard'
urlpatterns = [
    re_path(r'^$', dashboard.views.EmptyDashboardView.as_view(), name='empty'),
   re_path(r'^voip$', dashboard.views.VoipDashboardView.as_view(), name='voip'),
   re_path(r'^home$', dashboard.views.HomeDashboardView.as_view(), name='home'),
    path('register',dashboard.views.Registration.as_view(),name='register')
]
