from rest_framework import serializers

from apps.quizz.models import (
    SubCategory, TopLevelCategory, Category,
    Quiz, Question
)


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']


class TopLevelCategorySerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField()

    class Meta:
        model = TopLevelCategory
        fields = ['id', 'name', 'subcategory']

    def get_subcategory(self, obj):
        queryset = Category.objects.select_related('parent').filter(
            parent=obj
        )
        serializer = SubCategorySerializer(queryset, many=True)
        return serializer.data


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text']


class QuizSerializer(serializers.ModelSerializer):
    question_list = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'category', 'description', 'created_at', 'question_list']

    def get_question_list(self, obj):
        queryset = Question.objects.select_related('quiz').filter(
            quiz=obj
        )
        serializer = QuestionSerializer(queryset, many=True)
        return serializer.data
