# django
from django.contrib import admin
# local
from .models import *
from platforms.forms import BroadworksPlatformForm

@admin.register(BroadworksPlatform)
class BroadworksPlatformAdmin(admin.ModelAdmin):
    form = BroadworksPlatformForm
