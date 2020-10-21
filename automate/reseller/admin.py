from django.contrib import admin

from reseller.forms import ResellerPlatformForm
from reseller.models import ResellerPlatform


@admin.register(ResellerPlatform)
class BroadworksPlatformAdmin(admin.ModelAdmin):
    form = ResellerPlatformForm
