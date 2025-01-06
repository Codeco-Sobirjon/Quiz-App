from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from apps.quizz.models import (
    Category, TopLevelCategory, SubCategory,
    Quiz, Question
)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    search_fields = ('name',)
    ordering = ('created_at',)


@admin.register(TopLevelCategory)
class TopLevelCategoryAdmin(CategoryAdmin):
    list_display = ['name', 'created_at', 'id']
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
    list_display = ['name', 'parent', 'created_at', 'id']
    search_fields = ['name']

    def get_list_filter(self, request):
        return super().get_list_filter(request) + (('parent', admin.RelatedOnlyFieldListFilter),)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=False)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = Category.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class QuestionInlenes(admin.TabularInline):
    model = Question
    fields = ['text', 'is_correct']
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_category_name', 'created_at']
    search_fields = ['title']
    list_filter = ['category']
    inlines = [QuestionInlenes]

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    get_category_name.short_description = 'Категория'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(parent__isnull=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)