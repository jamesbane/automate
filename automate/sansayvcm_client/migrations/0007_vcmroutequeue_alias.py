# Generated by Django 2.2.8 on 2020-09-26 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sansayvcm_client', '0006_auto_20200925_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcmroutequeue',
            name='alias',
            field=models.CharField(default='Cust 40549 8057645350', max_length=64),
            preserve_default=False,
        ),
    ]