# Generated by Django 5.1.3 on 2025-01-06 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0003_alter_quiz_options_alter_question_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='title',
            field=models.TextField(blank=True, max_length=255, null=True, verbose_name='Название викторины'),
        ),
    ]
