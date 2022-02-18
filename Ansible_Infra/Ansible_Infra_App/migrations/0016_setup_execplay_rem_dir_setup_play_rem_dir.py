# Generated by Django 4.0.2 on 2022-02-13 01:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Ansible_Infra_App', '0015_setup_backup_directory_setup_palybooks_directory'),
    ]

    operations = [
        migrations.AddField(
            model_name='setup',
            name='execplay_rem_dir',
            field=models.CharField(default=datetime.datetime(2022, 2, 13, 1, 25, 1, 494860, tzinfo=utc), max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='setup',
            name='play_rem_dir',
            field=models.CharField(default=datetime.datetime(2022, 2, 13, 1, 25, 7, 327638, tzinfo=utc), max_length=150),
            preserve_default=False,
        ),
    ]