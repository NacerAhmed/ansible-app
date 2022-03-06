# Generated by Django 4.0.2 on 2022-03-02 22:01

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

  

    operations = [
        migrations.CreateModel(
            name='Playbook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('desc', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('ip', models.CharField(max_length=50)),
                ('superuser_name', models.CharField(max_length=50)),
                ('superuser_password', models.CharField(max_length=512)),
                ('group', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('master', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Setup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inventory', models.CharField(max_length=150)),
                ('config', models.CharField(max_length=150)),
                ('status', models.CharField(max_length=150)),
                ('backup_directory', models.CharField(max_length=150)),
                ('palybooks_directory', models.CharField(max_length=150)),
                ('play_rem_dir', models.CharField(max_length=150)),
                ('exec_play_rem_dir', models.CharField(max_length=150)),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ansible_Infra_App.server')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('desc', models.CharField(max_length=150)),
                ('status', models.CharField(max_length=150)),
                ('dir_path', models.CharField(max_length=150)),
                ('git_dir', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(default=None, upload_to='avatars/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('desc', models.CharField(max_length=150)),
                ('is_installed', models.BooleanField(default=False)),
                ('playbook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ansible_Infra_App.playbook')),
            ],
        ),
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=50)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Ansible_Infra_App.server')),
            ],
        ),
    ]
