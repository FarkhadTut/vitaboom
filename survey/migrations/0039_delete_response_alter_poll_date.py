# Generated by Django 4.0.4 on 2022-06-21 07:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0038_remove_response_answer_id_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Response',
        ),
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 21, 12, 0, 23, 471148)),
        ),
    ]
