# Generated by Django 5.1.4 on 2025-01-08 16:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0012_alter_uploadtests_options_uploadtests_author_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionoption',
            name='quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions_option', to='quizz.quizquestion', verbose_name='Викторина'),
        ),
    ]
