# Generated by Django 4.0.4 on 2022-06-23 07:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0058_alter_poll_date_alter_response_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 23, 12, 50, 55, 660612)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 23, 12, 50, 55, 661610)),
        ),
    ]
