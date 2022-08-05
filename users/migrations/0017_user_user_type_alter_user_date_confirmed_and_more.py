# Generated by Django 4.0.5 on 2022-07-02 13:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_remove_user_user_type_alter_user_date_confirmed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(default='employee', max_length=512),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='date_confirmed',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 7, 2, 18, 38, 10, 24375), null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_submitted',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 2, 18, 38, 10, 24375)),
        ),
    ]