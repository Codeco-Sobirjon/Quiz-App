# Generated by Django 5.1.4 on 2025-01-08 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0014_alter_questionoption_quiz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questionoption',
            options={'verbose_name': 'Вариант ответа', 'verbose_name_plural': 'Варианты ответа'},
        ),
        migrations.RemoveField(
            model_name='questionoption',
            name='quiz',
        ),
        migrations.AddField(
            model_name='questionoption',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='options', to='quizz.quizquestion', verbose_name='Вопрос'),
        ),
    ]