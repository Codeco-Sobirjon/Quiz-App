# Generated by Django 5.1.4 on 2025-01-08 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0009_alter_subcategory_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name': '2. Направление', 'verbose_name_plural': '2. Направление'},
        ),
        migrations.AlterModelOptions(
            name='toplevelcategory',
            options={'verbose_name': '1. Специальность', 'verbose_name_plural': '1. Специальность'},
        ),
    ]
