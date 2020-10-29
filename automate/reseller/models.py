from django.contrib.auth.models import Group
from django.db import models
from six import python_2_unicode_compatible


class ResellerManager(models.Manager):
    def as_choices(self):
        yield (self.pk, self.territory_name)


@python_2_unicode_compatible
class ResellerCount(models.Model):
    customer = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    territory_id = models.IntegerField()
    territory_name = models.CharField(max_length=255)
    count_for_limit = models.IntegerField()
    count_external = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    objects = ResellerManager()

    def __str__(self):
        return self.territory_name


class ResellerPlatform(models.Model):
    name = models.CharField(max_length=32, unique=True)
    username = models.CharField(max_length=1024)
    password = models.CharField(max_length=1024)
    client_id = models.CharField(max_length=1024)
    client_secret = models.CharField(max_length=1024)
    customer = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
