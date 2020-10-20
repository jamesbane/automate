from django.conf import settings
from django.db import models


class ResellerCount(models.Model):
    territory_id = models.IntegerField()
    territory_name = models.CharField(max_length=255)
    count_for_limit = models.IntegerField()
    count_external = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
