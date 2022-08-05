# Generated by Django 4.0.4 on 2022-06-22 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_authentication_remove_user_is_admin_user_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirmed',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='authentication',
            name='user_type',
            field=models.CharField(blank=True, choices=[('employee', 'Employee'), ('admin', 'Admin')], max_length=512, null=True),
        ),
    ]
