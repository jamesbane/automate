# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-29 15:02
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth import get_user_model


def update_users(apps, schema_editor):
    Profile = apps.get_model("steward", "Profile")
    User = get_user_model()

    for user in User.objects.all():
       if not hasattr(user, 'profile'):
            Profile.objects.create(user_id=user.id)


class Migration(migrations.Migration):

    dependencies = [
        ('steward', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_users),
    ]
