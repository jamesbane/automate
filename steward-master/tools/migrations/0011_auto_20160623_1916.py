# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-06-23 19:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0010_auto_20160610_2007'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='process',
            options={'ordering': ['-start_timestamp', '-end_timestamp'], 'permissions': (('process_call_park_pickup_configurator_exec', 'Call Park/Pickup Configurator Execute'), ('process_call_park_pickup_configurator_view', 'Call Park/Pickup Configurator View Results'), ('process_device_specific_migration_exec', 'Device Specific Migration Execute'), ('process_device_specific_migration_view', 'Device Specific Migration View Results'), ('process_firmware_report_exec', 'Firmware Report Execute'), ('process_firmware_report_view', 'Firmware Report View Results'), ('process_fraud_compliance_reset_exec', 'Fraud Compliance Reset Tool Execute'), ('process_fraud_compliance_reset_view', 'Fraud Compliance Reset Tool View Results'), ('process_lab_rebuild_exec', 'Lab Rebuild Execute'), ('process_lab_rebuild_view', 'Lab Rebuild View Results'), ('process_ptt_configurator_exec', 'Push To Talk Configurator Execute'), ('process_ptt_configurator_view', 'Push To Talk Configurator View Results'), ('process_registration_by_type_exec', 'Registration by Type Report Execute'), ('process_registration_by_type_view', 'Registration by Type Report View Results'), ('process_registration_report_exec', 'Registration Report Execute'), ('process_registration_report_view', 'Registration Report View Results'), ('process_tag_report_exec', 'Tag Report Execute'), ('process_tag_report_view', 'Tag Report View Results'), ('process_tag_removal_exec', 'Tag Removal Tool Execute'), ('process_tag_removal_view', 'Tag Removal Tool View Results'), ('process_trunk_user_audit_exec', 'Trunk Audit Execute'), ('process_trunk_user_audit_view', 'Trunk Audit View Results'))},
        ),
    ]
