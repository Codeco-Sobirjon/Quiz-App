# Generated by Django 5.1.4 on 2025-01-11 15:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0021_questionoption_is_selected_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertestanswers',
            name='test_list',
        ),
        migrations.AddField(
            model_name='usertestanswers',
            name='quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_test_answer_quiz', to='quizz.quiz', verbose_name='Тест'),
        ),
        migrations.CreateModel(
            name='TestAnswerQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_answer_question', to='quizz.quizquestion', verbose_name='Вопрос')),
                ('test_answer_quiz', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_answer_question', to='quizz.usertestanswers', verbose_name='Тест')),
            ],
        ),
        migrations.CreateModel(
            name='TestAnswerQuestionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_answer_question_option', to='quizz.questionoption', verbose_name='Вопрос')),
                ('test_answer_question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='test_answer_question_options', to='quizz.testanswerquestion', verbose_name='Вопрос')),
            ],
        ),
        migrations.AddField(
            model_name='testanswerquestion',
            name='selected_answer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quizz.testanswerquestionoption'),
        ),
    ]