from rest_framework import serializers

from apps.quizz.models import (
    SubCategory, TopLevelCategory, Category,
    Quiz, QuestionOption, QuestionOption, OrderQuiz, QuizQuestion, TestAnswerQuestion, UserTestAnswers
)


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'slug']


class TopLevelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TopLevelCategory
        fields = ['id', 'name', 'slug']


class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'is_correct']


class QuizQuestionSerializer(serializers.ModelSerializer):
    option_list = serializers.SerializerMethodField()

    class Meta:
        model = QuizQuestion
        fields = ['id', 'title', 'created_at', 'selected_answer', 'option_list']

    def get_option_list(self, obj):
        instance = QuestionOption.objects.select_related('question').filter(question=obj).order_by('?')
        serializer = QuizOptionSerializer(instance, many=True, context={"request": self.context.get('request')})
        return serializer.data


class QuizSerializer(serializers.ModelSerializer):
    degree = serializers.SerializerMethodField()
    has_bought = serializers.SerializerMethodField()
    semester = serializers.SerializerMethodField()
    mode_of_study = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'price', 'semester', 'mode_of_study', 'year',
                  'degree', 'created_at', 'has_bought']

    def get_has_bought(self, obj):
        try:
            if OrderQuiz.objects.select_related('author').filter(
                    author=self.context.get('request').user).select_related('quiz').filter(quiz=obj).exists():
                return True
        except:
            return False
        return False

    def get_semester(self, obj):
        return obj.get_semester_display() if obj.semester else None

    def get_mode_of_study(self, obj):
        return obj.get_mode_of_study_display() if obj.mode_of_study else None

    def get_year(self, obj):
        return obj.get_year_display() if obj.year else None

    def get_degree(self, obj):
        if obj.category and obj.category.parent:
            return SubCategorySerializer(obj.category.parent).data
        return None


class TestAnswerQuestionSerializer(serializers.ModelSerializer):
    option_list = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    selected_answer = QuizOptionSerializer(read_only=True)

    class Meta:
        model = TestAnswerQuestion
        fields = ['id', 'title', 'selected_answer', 'option_list']

    def get_option_list(self, obj):
        instance = QuestionOption.objects.select_related('question').filter(question=obj.question).order_by('?')
        serializer = QuizOptionSerializer(instance, many=True, context={"request": self.context.get('request')})
        return serializer.data

    def get_title(self, obj):
        return obj.question.title


class UserTestAnswersListSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    test_list = serializers.SerializerMethodField()

    class Meta:
        model = UserTestAnswers
        fields = [
            'id', 'quiz', 'created_at', 'test_list'
        ]

    def get_test_list(self, obj):
        queryset = TestAnswerQuestion.objects.select_related('test_answer_quiz').filter(
            test_answer_quiz=obj
        )
        serializer = TestAnswerQuestionSerializer(queryset, many=True, context={
            'request': self.context.get('request')
        })
        return serializer.data
