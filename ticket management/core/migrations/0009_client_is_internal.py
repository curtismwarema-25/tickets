# Generated by Django 5.0.14 on 2025-07-07 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_client_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='is_internal',
            field=models.BooleanField(default=False),
        ),
    ]
