from django.db import models
from django.utils.translation import gettext as _
from django_ckeditor_5.fields import CKEditor5Field
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.account.models import CustomUser


class Category(models.Model):
    name = models.CharField(_("Название категория"), max_length=250, null=True, blank=True)  # Removed the comma here
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Родитель категории",
        related_name='subcategories'
    )
    created_at = models.DateField(auto_now_add=True, null=True, blank=True, verbose_name="Дата публикации")

    objects = models.Manager()

    def __str__(self):
        str_name = self.name or _("Без названия")
        parent = self.parent

        while parent:
            parent_name = parent.name or _("Без названия")
            str_name = f'{parent_name} / ' + str_name
            parent = parent.parent

        return str_name


class TopLevelCategory(Category):
    class Meta:
        proxy = True
        verbose_name = "1. Основная категория"
        verbose_name_plural = "1. Основная категория"


class SubCategory(Category):
    class Meta:
        proxy = True
        verbose_name = "2. Подкатегория"
        verbose_name_plural = "2. Подкатегория"


class Quiz(models.Model):
    title = models.TextField(max_length=255, null=True, blank=True, verbose_name='Название викторины')
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name="Категория", related_name='category')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Дата создания')

    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '3. Тест'
        verbose_name_plural = '3. Тести'


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True,
                             verbose_name='Викторина')
    text = models.TextField(max_length=500, verbose_name='Текст вопроса')
    is_correct = models.BooleanField(default=False, null=True, blank=True, verbose_name='Правильный ответ')

    objects = models.Manager()

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
