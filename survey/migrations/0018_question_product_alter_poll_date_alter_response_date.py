# Generated by Django 4.0.5 on 2022-06-19 10:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0017_alter_poll_date_alter_response_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='product',
            field=models.CharField(blank=True, choices=[('products_type', 'Products type'), ('products_product', 'Product name'), ('products_identifier', 'Products identifier'), (None, 'None')], max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 15, 48, 37, 15341)),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 19, 15, 48, 37, 30957)),
        ),
    ]
