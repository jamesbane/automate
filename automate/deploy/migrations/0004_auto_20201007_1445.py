# Generated by Django 2.2.8 on 2020-10-07 14:45

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0003_auto_20200713_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetype',
            name='skus',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=32), blank=True, default=dict, size=None),
        ),
    ]
