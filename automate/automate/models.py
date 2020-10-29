import pytz
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import Group
from django.db import models

from reseller.models import ResellerPlatform


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=256, default='America/New_York',
                                choices=((x, x) for x in pytz.country_timezones['US']))


class GroupDefaultView(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    priority = models.PositiveSmallIntegerField()
    view_name = models.CharField(max_length=256)


def has_reseller_perms(self):
    reseller_platforms = ResellerPlatform.objects.all()
    customer_ids = [item.customer.id for item in reseller_platforms]
    groups = self.groups.all()
    group_ids = [item.id for item in groups]
    for customer_id in customer_ids:
        if customer_id in group_ids:
            return True
    return False


auth.models.User.add_to_class('has_reseller_perms', has_reseller_perms)
