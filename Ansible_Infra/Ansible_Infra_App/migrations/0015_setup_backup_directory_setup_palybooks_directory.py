# Generated by Django 4.0.2 on 2022-02-12 20:49

import datetime
from django.db import migrations, models
from django.utils.timezone import utc
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Ansible_Infra_App', '0014_setup'),
    ]

    operations = [
        migrations.AddField(
            model_name='setup',
            name='backup_directory',
            field=models.CharField(default=django.utils.timezone.now, max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='setup',
            name='palybooks_directory',
            field=models.CharField(default=datetime.datetime(2022, 2, 12, 20, 49, 56, 268110, tzinfo=utc), max_length=150),
            preserve_default=False,
        ),
    ]