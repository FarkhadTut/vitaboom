# Generated by Django 4.0.5 on 2022-06-18 18:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0005_alter_poll_date_alter_response_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 18, 23, 57, 47, 434062)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 18, 23, 57, 47, 434062)),
        ),
    ]
