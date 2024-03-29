# Generated by Django 4.0.5 on 2022-06-18 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_record_units'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='amount',
            new_name='quantity',
        ),
        migrations.AddField(
            model_name='record',
            name='volume',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='record',
            name='units',
            field=models.CharField(choices=[('dona', 'Dona'), ('korobka', 'Korobka'), ('qop', 'Qop')], max_length=512),
        ),
    ]
