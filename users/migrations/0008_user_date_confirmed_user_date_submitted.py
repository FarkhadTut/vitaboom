# Generated by Django 4.0.4 on 2022-06-23 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_user_date_confirmed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='date_confirmed',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='date_submitted',
            field=models.DateTimeField(default='a'),
            preserve_default=False,
        ),
    ]
