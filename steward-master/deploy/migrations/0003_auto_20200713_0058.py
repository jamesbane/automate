# Generated by Django 2.2.8 on 2020-07-12 23:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0002_auto_20160608_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devices', to='deploy.DeviceType'),
        ),
        migrations.AlterField(
            model_name='device',
            name='site',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devices', to='deploy.Site'),
        ),
    ]
