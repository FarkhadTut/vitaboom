# Generated by Django 4.0.5 on 2022-07-02 15:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0065_alter_poll_date_alter_question_show_users_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='show_users',
        ),
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 2, 20, 14, 15, 882976)),
        ),
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('single', 'Single choice'), ('multiple', 'Multiple choice'), ('open', 'Open question'), ('location', 'Location'), ('integer', 'Integer'), ('image', 'Image'), ('password', 'Password'), ('action', 'Action'), ('price', 'Price'), ('payment', 'Payment'), ('unit', 'Unit'), ('product', 'Product'), ('quantity', 'Quantity'), ('volume', 'Volume'), ('contact', 'Contact'), ('users', 'Users')], max_length=128),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 2, 20, 14, 15, 882976)),
        ),
    ]
