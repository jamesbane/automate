# Generated by Django 2.2.8 on 2020-08-28 07:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('platforms', '0006_auto_20200827_1809'),
    ]

    operations = [
        migrations.RenameField(
            model_name='broadworksplatform',
            old_name='user',
            new_name='customer',
        ),
        migrations.AddField(
            model_name='broadworksplatform',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group'),
        ),
    ]
