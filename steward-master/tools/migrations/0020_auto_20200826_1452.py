# Generated by Django 2.2.8 on 2020-08-26 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0019_auto_20200713_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='start_timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
