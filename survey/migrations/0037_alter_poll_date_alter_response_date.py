# Generated by Django 4.0.4 on 2022-06-21 06:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0036_rename_answerss_id_response_answer_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 21, 11, 59, 2, 976548)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 21, 11, 59, 2, 976548)),
        ),
    ]
