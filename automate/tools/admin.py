from django.contrib import admin

from tools.models import Process

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    pass