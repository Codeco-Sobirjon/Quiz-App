# Generated by Django 5.1.4 on 2025-01-09 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0018_alter_quiz_mode_of_study'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, null=True, unique=True, verbose_name='Слаг'),
        ),
    ]