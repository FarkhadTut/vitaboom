# Generated by Django 4.0.5 on 2022-06-18 19:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0011_alter_answer_next_question_alter_poll_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 0, 55, 2, 28568)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 0, 55, 2, 28568)),
        ),
    ]
