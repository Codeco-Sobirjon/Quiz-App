from django import forms
from django.contrib import admin
from django.db import models
import nested_admin
from apps.quizz.models import (
    Category, TopLevelCategory, SubCategory,
    Quiz, QuestionOption, OrderQuiz, QuizQuestion, UploadTests, UserTestAnswers,
    TestAnswerQuestion
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    search_fields = ('name',)
    ordering = ('created_at',)


@admin.register(TopLevelCategory)
class TopLevelCategoryAdmin(CategoryAdmin):
    list_display = ['name', 'slug', 'created_at', 'id']
    search_fields = ['name']

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'parent' in fields:
            fields.remove('parent')
        return fields

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=True)


@admin.register(SubCategory)
class SubCategoryAdmin(CategoryAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at', 'id']
    search_fields = ['name']

    def get_list_filter(self, request):
        return super().get_list_filter(request) + (('parent', admin.RelatedOnlyFieldListFilter),)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = Category.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class QuestionOptionInline(nested_admin.NestedTabularInline):
    model = QuestionOption
    fields = ['text', 'is_correct']
    extra = 1
    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'cols': 40, 'rows': 3})}
    }


class QuizQuestionInline(nested_admin.NestedTabularInline):
    model = QuizQuestion
    fields = ['title']
    extra = 1
    inlines = [QuestionOptionInline]

    formfield_overrides = {
        models.CharField: {'widget': forms.Textarea(attrs={'cols': 40, 'rows': 3})}
    }


@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title', 'get_category_name', 'created_at']
    search_fields = ['title']
    list_filter = ['category']
    inlines = [QuizQuestionInline]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    get_category_name.short_description = 'Категория'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(parent__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(UploadTests)
class UploadTestsAdmin(admin.ModelAdmin):
    list_display = ['quiz__title', 'author', 'created_at']
    search_fields = ['quiz__title']


@admin.register(OrderQuiz)
class OrderQuizAdmin(admin.ModelAdmin):
    list_display = ['quiz__title', 'author', 'created_at']
    search_fields = ['quiz__title']


class TestAnswerQuestionInline(nested_admin.NestedTabularInline):
    model = TestAnswerQuestion
    fields = ['question', 'selected_answer']
    extra = 1


@admin.register(UserTestAnswers)
class UserTestAnswersAdmin(nested_admin.NestedModelAdmin):
    list_display = ['author']
    inlines = [TestAnswerQuestionInline]


@admin.register(TestAnswerQuestion)
class TestAnswerQuestionadmin(admin.ModelAdmin):
    pass