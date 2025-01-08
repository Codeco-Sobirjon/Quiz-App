from rest_framework import serializers

from apps.quizz.models import (
    SubCategory, TopLevelCategory, Category,
    Quiz, QuestionOption, QuestionOption, OrderQuiz, QuizQuestion
)


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']


class TopLevelCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = TopLevelCategory
        fields = ['id', 'name']


class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'is_correct']


class QuizQuestionSerializer(serializers.ModelSerializer):
    option_list = serializers.SerializerMethodField()

    class Meta:
        model = QuizQuestion
        fields = ['id', 'title', 'created_at', 'option_list']

    def get_option_list(self, obj):

        instance = QuestionOption.objects.select_related('question').filter(question=obj)
        serializer = QuizOptionSerializer(instance, many=True, context={"request": self.context.get('request')})
        return serializer.data



class QuizSerializer(serializers.ModelSerializer):
    category = SubCategorySerializer(read_only=True)
    is_buying = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'price', 'semester', 'mode_of_study', 'year',
                  'category', 'created_at', 'is_buying']

    def get_is_buying(self, obj):
        try:
            if OrderQuiz.objects.select_related('author').filter(author=self.context.get('request').user).select_related('quiz').filter(quiz=obj).exists():
                return True
        except:
            return False
        return False
