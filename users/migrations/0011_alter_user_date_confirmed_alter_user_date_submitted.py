# Generated by Django 4.0.4 on 2022-06-23 07:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_user_date_confirmed_user_date_submitted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_confirmed',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 6, 23, 12, 50, 37, 493220), null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_submitted',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 23, 12, 50, 37, 493220)),
        ),
    ]
