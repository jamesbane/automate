from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save


class BroadworksPlatform(models.Model):
    name = models.CharField(max_length=32, unique=True)
    uri = models.CharField(max_length=1024)
    username = models.CharField(max_length=256)
    password = models.CharField(max_length=256)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class PlatformPermission(models.Model):
    platform = models.OneToOneField(BroadworksPlatform,on_delete=models.CASCADE)
    permission = models.ForeignKey(Group,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.platform.name 

class PlatformUsers(models.Model):
    platform = models.OneToOneField(BroadworksPlatform,on_delete=models.CASCADE)
    users = models.ManyToManyField(User)
    
    def __str__(self):
        return self.platform.name

def set_user_permission(sender, instance, **kwargs):
    try:
        from tools.models import Process
        perm = PlatformPermission.objects.filter(platform=instance.platform).first()
        print(instance.users.all())
        for user in instance.users.all():
            for p in perm.permission.permissions.all():
                user.user_permissions.add(p) 
                if not Process.objects.filter(user = user,
                platform_type=perm.platform.id,view_permission=p.name).exists():
                    print("here")
                    Process(user=user,
                    method='web',
                    platform_type=perm.platform.id,
                    platform_id = 1,
                    parameters={},
                    status=0,
                    view_permission=p.name).save()
    except Exception as e:
        print(e)

post_save.connect(set_user_permission, sender=PlatformUsers)