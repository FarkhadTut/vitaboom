# Generated by Django 4.0.4 on 2022-06-23 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_date_confirmed_user_date_submitted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='date_confirmed',
        ),
        migrations.RemoveField(
            model_name='user',
            name='date_submitted',
        ),
    ]
