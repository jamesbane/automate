from datetime import datetime
from django.db import models

class SansayVcmServer(models.Model):
    name = models.CharField(max_length=32, unique=True)
    uri = models.CharField(max_length=1021)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    client_id = models.IntegerField()
    
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class SansayCluster(models.Model):
    server = models.ForeignKey(SansayVcmServer, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, unique=True)
    cluster_id = models.IntegerField()
    route_table = models.CharField(max_length=32)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class RouteTableLog(models.Model):
    cluster = models.ForeignKey(SansayCluster, on_delete=models.CASCADE)
    number = models.CharField(max_length=64)
    action = models.CharField(max_length=32)
    xmlcfg = models.TextField(null=True)
    result_status = models.CharField(max_length=32)
    result_data = models.TextField(null=True)
    created = models.DateTimeField(null=True, default=None)
    
    class Meta:
        ordering = ('-created',)

class VcmRouteQueue(models.Model):
    uuid = models.IntegerField()
    number = models.CharField(max_length=64)
    alias = models.CharField(max_length=64)
    action = models.CharField(max_length=32)
    create_date = models.DateTimeField(null=False, default=datetime.now)
    xmlcfg = models.TextField(null=False)
    status = models.CharField(max_length=20)
    cluster = models.ForeignKey(SansayCluster, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-create_date',)

    def get_status(self):
        return self.status.capitalize()
