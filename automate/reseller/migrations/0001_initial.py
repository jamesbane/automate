# Generated by Django 2.2.8 on 2020-10-19 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ResellerGroup',
            fields=[
                ('group_id', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('interval', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResellerCount',
            fields=[
                ('id', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('territory_id', models.IntegerField()),
                ('territory_name', models.CharField(max_length=255)),
                ('count_for_limit', models.IntegerField()),
                ('count_external', models.IntegerField()),
                ('reseller_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reseller.ResellerGroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
