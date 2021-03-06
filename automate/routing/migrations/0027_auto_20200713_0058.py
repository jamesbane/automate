# Generated by Django 2.2.8 on 2020-07-12 23:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routing', '0026_auto_20181221_0505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fraudbypasshistory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='number',
            name='route',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='numbers', to='routing.Route'),
        ),
        migrations.AlterField(
            model_name='numberhistory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='outboundroute',
            name='end_office_route',
            field=models.ForeignKey(limit_choices_to={'type': 1}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='routing.Route'),
        ),
        migrations.AlterField(
            model_name='outboundroute',
            name='long_distance_route',
            field=models.ForeignKey(limit_choices_to={'type': 1}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='routing.Route'),
        ),
        migrations.AlterField(
            model_name='outboundroutehistory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='record',
            name='route',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='records', to='routing.Route'),
        ),
        migrations.AlterField(
            model_name='remotecallforwardhistory',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
