# Generated by Django 4.0.4 on 2022-06-21 06:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0034_rename_response_id_response_answer_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='response',
            old_name='answer_id',
            new_name='answerss_id',
        ),
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 21, 11, 58, 25, 824341)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 21, 11, 58, 25, 824341)),
        ),
    ]