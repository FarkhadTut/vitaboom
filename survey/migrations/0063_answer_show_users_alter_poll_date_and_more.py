# Generated by Django 4.0.5 on 2022-07-02 13:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0062_alter_poll_date_alter_response_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='show_users',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 2, 18, 38, 10, 8727)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 2, 18, 38, 10, 8727)),
        ),
    ]