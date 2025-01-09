from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.validators import FileExtensionValidator


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
        verbose_name = "1. Специальность"
        verbose_name_plural = "1. Специальность"


class SubCategory(Category):
    class Meta:
        proxy = True
        verbose_name = "2. Направление"
        verbose_name_plural = "2. Направление"


class Quiz(models.Model):
    SEMESTER_CHOICES = [
        ('1', _("I")),
        ('2', _("II")),
    ]

    MODE_OF_STUDY_CHOICES = [
        ('daytime', _("Kunduzki")),
        ('evening', _("Sirtqi")),
        ('remote', _("Masofaviy")),
        ('external', _("Tashqi")),
    ]

    YEAR_CHOICES = [
        ('1', _("I")),
        ('2', _("II")),
        ('3', _("III")),
        ('4', _("IV")),
        ('5', _("V")),
        ('6', _("VI")),
    ]

    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Название теста"))
    price = models.FloatField(default=0, null=True, blank=True, verbose_name=_("Цена"))
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, null=True, blank=True,
                                verbose_name=_("Семестр"))
    mode_of_study = models.CharField(
        max_length=10, choices=MODE_OF_STUDY_CHOICES, null=True, blank=True, verbose_name=_("Форма обучения")
    )
    year = models.CharField(max_length=2, choices=YEAR_CHOICES, null=True, blank=True, verbose_name=_("Год обучения"))

    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name="Категория", related_name='category')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Дата создания"))

    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '3. Название теста'
        verbose_name_plural = '3. Название теста'


class UploadTests(models.Model):
    file = models.FileField(upload_to='test/', null=True, blank=True, verbose_name="Загрузить файл",
                            validators=[FileExtensionValidator(allowed_extensions=['txt'])])
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='upload_quiz', null=True, blank=True,
                             verbose_name='Викторина')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Автор", related_name="author_upload")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return self.quiz.title

    class Meta:
        verbose_name = '4. Загрузить файл'
        verbose_name_plural = '4. Загрузить файл'


class OrderQuiz(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='order_quiz', null=True, blank=True,
                             verbose_name='Викторина')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Автор", related_name="author_order")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return self.quiz.title

    class Meta:
        verbose_name = '5. Заказать тест'
        verbose_name_plural = '5. Заказать тест'


class QuizQuestion(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Название теста"))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="Тест", related_name='test')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("Дата создания"))

    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '3. Тест'
        verbose_name_plural = '3. Тести'


class QuestionOption(models.Model):
    question = models.ForeignKey(
        QuizQuestion, on_delete=models.CASCADE, related_name='options', null=True, blank=True, verbose_name='Вопрос'
    )
    text = models.CharField(max_length=500, verbose_name='Текст вопроса', null=True, blank=True)
    is_correct = models.BooleanField(default=False, null=True, blank=True, verbose_name='Правильный ответ')

    objects = models.Manager()

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'
