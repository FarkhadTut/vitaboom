# Generated by Django 4.0.5 on 2022-07-04 15:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_remove_product_identifier_alter_identifier_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='identifier',
            old_name='type',
            new_name='product',
        ),
    ]
