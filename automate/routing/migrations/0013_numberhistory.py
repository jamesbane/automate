# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-25 17:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('routing', '0012_remove_number_destination'),
    ]

    operations = [
        migrations.CreateModel(
            name='NumberHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cc', models.SmallIntegerField(default=1)),
                ('number', models.CharField(max_length=64)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=256)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('modified',),
            },
        ),
    ]
