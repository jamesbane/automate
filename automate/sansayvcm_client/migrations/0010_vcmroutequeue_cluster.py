# Generated by Django 2.2.8 on 2020-11-18 01:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sansayvcm_client', '0009_auto_20201003_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcmroutequeue',
            name='cluster',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='sansayvcm_client.SansayCluster'),
            preserve_default=False,
        ),
    ]
