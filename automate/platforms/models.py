from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save


class BroadworksPlatform(models.Model):
    name = models.CharField(max_length=32, unique=True)
    uri = models.CharField(max_length=1024)
    username = models.CharField(max_length=1024)
    password = models.CharField(max_length=1024)
    customer = models.ForeignKey(Group,on_delete=models.CASCADE,null=True)


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


def set_user_permission(sender, instance, **kwargs):
    try:
        from tools.models import Process
        users = User.objects.filter(groups__id = instance.customer.id)
        print(users)
        for user in users:
            for p in instance.customer.permissions.all():
                user.user_permissions.add(p)
                if not Process.objects.filter(user = user,
                platform_type=instance.id,view_permission=p.name).exists():
                    Process(user=user,
                    method='web',
                    platform_type=instance.id,
                    platform_id = instance,
                    parameters={},
                    status=0,
                    view_permission=p.name).save()
    except Exception as e:
        print('#################')
        print(e)

post_save.connect(set_user_permission, sender=BroadworksPlatform)