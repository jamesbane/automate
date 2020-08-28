# django
from django.contrib import admin
# local
from .models import *


# Register your models here.
admin.site.register(BroadworksPlatform, admin.ModelAdmin)
admin.site.register(PlatformPermission)
admin.site.register(PlatformUsers)
