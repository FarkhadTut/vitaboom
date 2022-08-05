# Generated by Django 4.0.4 on 2022-06-20 15:25

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0021_alter_poll_date_alter_question_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 20, 20, 25, 0, 707514)),
        ),
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('single', 'Single choice'), ('multiple', 'Multiple choice'), ('open', 'Open question'), ('location', 'Location'), ('integer', 'Integer'), ('image', 'Image'), ('password', 'Password'), ('action', 'Action'), ('price', 'Price'), ('payment', 'Payment'), ('unit', 'Unit'), ('product', 'Product'), ('quantity', 'Quantity'), ('volume', 'Volume')], max_length=128),
        ),
        migrations.AlterField(
            model_name='response',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 20, 20, 25, 0, 707514)),
        ),
        migrations.CreateModel(
            name='OpenAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='survey.answer')),
                ('question', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='survey.question')),
            ],
        ),
    ]