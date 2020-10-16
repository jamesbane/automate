# Generated by Django 2.2.8 on 2020-09-04 16:25

import automate.storage
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('platforms', '0008_auto_20200828_0725'),
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=256)),
                ('platform_type', models.SmallIntegerField()),
                ('parameters', django.contrib.postgres.fields.jsonb.JSONField()),
                ('start_timestamp', models.DateTimeField(auto_now=True)),
                ('end_timestamp', models.DateTimeField(null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Scheduled'), (1, 'Completed'), (2, 'Cancled'), (3, 'Error'), (4, 'Running')], default=0)),
                ('exception', models.TextField()),
                ('view_permission', models.CharField(db_index=True, max_length=64)),
                ('platform_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platforms.BroadworksPlatform')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='processes', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ['-start_timestamp', '-end_timestamp'],
                'permissions': (('process_busy_lamp_field_fixup_exec', 'Busy Lamp Field Fixup Execute'), ('process_busy_lamp_field_fixup_view', 'Busy Lamp Field Fixup View Results'), ('process_call_park_pickup_configurator_exec', 'Call Park/Pickup Configurator Execute'), ('process_call_park_pickup_configurator_view', 'Call Park/Pickup Configurator View Results'), ('process_dect_configurator_exec', 'DECT Configurator Execute'), ('process_dect_configurator_view', 'DECT Configurator View Results'), ('process_device_specific_migration_exec', 'Device Specific Migration Execute'), ('process_device_specific_migration_view', 'Device Specific Migration View Results'), ('process_firmware_report_exec', 'Firmware Report Execute'), ('process_firmware_report_view', 'Firmware Report View Results'), ('process_fraud_compliance_reset_exec', 'Fraud Compliance Reset Tool Execute'), ('process_fraud_compliance_reset_view', 'Fraud Compliance Reset Tool View Results'), ('process_lab_rebuild_exec', 'Lab Rebuild Execute'), ('process_lab_rebuild_view', 'Lab Rebuild View Results'), ('process_ptt_configurator_exec', 'Push To Talk Configurator Execute'), ('process_ptt_configurator_view', 'Push To Talk Configurator View Results'), ('process_registration_by_type_exec', 'Registration by Type Report Execute'), ('process_registration_by_type_view', 'Registration by Type Report View Results'), ('process_registration_report_exec', 'Registration Report Execute'), ('process_registration_report_view', 'Registration Report View Results'), ('process_speed_dial_configurator_exec', 'Speed Dial Configurator Execute'), ('process_speed_dial_configurator_view', 'Speed Dial Configurator View Results'), ('process_tag_removal_exec', 'Tag Removal Tool Execute'), ('process_tag_removal_view', 'Tag Removal Tool View Results'), ('process_tag_report_exec', 'Tag Report Execute'), ('process_tag_report_view', 'Tag Report View Results'), ('process_trunk_user_audit_exec', 'Trunk Audit Execute'), ('process_trunk_user_audit_view', 'Trunk Audit View Results')),
            },
        ),
        migrations.CreateModel(
            name='ProcessContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tab', models.CharField(max_length=32)),
                ('priority', models.PositiveSmallIntegerField(default=32767)),
                ('raw', models.FileField(storage=automate.storage.ProtectedFileStorage(), upload_to='process')),
                ('html', models.FileField(storage=automate.storage.ProtectedFileStorage(), upload_to='process')),
                ('process', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='tools.Process')),
            ],
            options={
                'ordering': ['priority', 'tab'],
            },
        ),
    ]
