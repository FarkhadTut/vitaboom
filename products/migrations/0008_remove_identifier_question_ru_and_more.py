# Generated by Django 4.0.5 on 2022-06-19 10:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_rename_question_identifier_question_ru_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='identifier',
            name='question_ru',
        ),
        migrations.RemoveField(
            model_name='identifier',
            name='question_uz',
        ),
        migrations.RemoveField(
            model_name='product',
            name='question_ru',
        ),
        migrations.RemoveField(
            model_name='product',
            name='question_uz',
        ),
        migrations.RemoveField(
            model_name='type',
            name='question_ru',
        ),
        migrations.RemoveField(
            model_name='type',
            name='question_uz',
        ),
    ]
