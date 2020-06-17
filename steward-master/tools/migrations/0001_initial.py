# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-25 15:44
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion

from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        HStoreExtension(),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=256)),
                ('parameters', django.contrib.postgres.fields.hstore.HStoreField()),
                ('start_timestamp', models.DateTimeField()),
                ('end_timestamp', models.DateTimeField(null=True)),
                ('content', django.contrib.postgres.fields.hstore.HStoreField()),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Scheduled'), (1, 'Completed'), (2, 'Cancled'), (3, 'Error')], default=0)),
                ('exception', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processes', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ['-start_timestamp', '-end_timestamp'],
            },
        ),
    ]
