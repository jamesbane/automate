from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save


class BroadworksPlatform(models.Model):
    name = models.CharField(max_length=32, unique=True)
    uri = models.CharField(max_length=1024)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


def set_user_permission(sender, instance, **kwargs):
    try:
        from tools.models import Process
        for p in instance.user.user_permissions.all():
            print(p.codename)
            if not Process.objects.filter(user = instance.user,
            platform_type=instance.id,view_permission=p.name).exists():
                Process(user=instance.user,
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