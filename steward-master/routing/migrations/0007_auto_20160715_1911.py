# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-15 19:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routing', '0006_auto_20160701_1427'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checksum', models.CharField(blank=True, max_length=32)),
                ('last_modified', models.DateTimeField(default=None, null=True)),
                ('result_state', models.IntegerField(choices=[(0, 'Success'), (1, 'Failure')])),
                ('result_data', models.TextField()),
                ('result_timestamp', models.DateTimeField(default=None, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='number',
            options={'ordering': ('modified',)},
        ),
        migrations.AddField(
            model_name='route',
            name='trunkgroup',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
    ]
