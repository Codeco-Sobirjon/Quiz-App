# Generated by Django 5.1.4 on 2025-01-16 05:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0026_alter_testanswerquestion_selected_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testanswerquestion',
            name='test_answer_quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author_test_answer_question', to='quizz.usertestanswers', verbose_name='Тест'),
        ),
    ]