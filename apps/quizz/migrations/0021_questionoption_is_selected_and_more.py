# Generated by Django 5.1.4 on 2025-01-10 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0020_usertestanswers'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionoption',
            name='is_selected',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Выбрано'),
        ),
        migrations.AddField(
            model_name='quizquestion',
            name='selected_answer',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Выбранный ответ'),
        ),
    ]
