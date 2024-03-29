# Generated by Django 4.0.5 on 2022-06-18 19:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_alter_poll_date_alter_response_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='next_question',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 0, 49, 29, 131945)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 0, 49, 29, 131945)),
        ),
    ]
