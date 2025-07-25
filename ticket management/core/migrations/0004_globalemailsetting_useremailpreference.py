# Generated by Django 5.0.14 on 2025-07-05 10:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_message_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalEmailSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Global Email Setting',
                'verbose_name_plural': 'Global Email Setting',
            },
        ),
        migrations.CreateModel(
            name='UserEmailPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_on_assignment', models.BooleanField(default=True)),
                ('notify_on_completion', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
