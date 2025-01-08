# Generated by Django 5.1.4 on 2025-01-08 07:31

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizz', '0010_alter_subcategory_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quiz',
            options={'verbose_name': '3. Название теста', 'verbose_name_plural': '3. Название теста'},
        ),
        migrations.CreateModel(
            name='UploadTests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='test/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['txt'])], verbose_name='Загрузить файл')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('quiz', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upload_quiz', to='quizz.quiz', verbose_name='Викторина')),
            ],
            options={
                'verbose_name': '3. Загрузить файл',
                'verbose_name_plural': '3. Загрузить файл',
            },
        ),
    ]
