# Generated by Django 5.1.3 on 2025-01-06 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_rename_first_name_customuser_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default=1, max_length=100, unique=True, verbose_name='Логин'),
            preserve_default=False,
        ),
    ]
