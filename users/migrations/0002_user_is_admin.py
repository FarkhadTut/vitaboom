# Generated by Django 4.0.4 on 2022-06-22 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
