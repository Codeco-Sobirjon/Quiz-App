from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from apps.quizz.models import (
    SubCategory, TopLevelCategory, UserTestAnswers,
    Quiz, QuestionOption, QuizQuestion, OrderQuiz, TestAnswerQuestion
)
import os
from django.conf import settings

from apps.quizz.pagination import QuizPagination
from apps.quizz.serializers import TopLevelCategorySerializer, QuizSerializer, SubCategorySerializer, \
    QuizQuestionSerializer, TestAnswerQuestionSerializer, UserTestAnswersListSerializer, TestResultSerializer
from apps.quizz.utils import import_tests_from_file


class TopLevelCategoryAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Categories'],
        operation_summary="Get all top-level categories with subcategories.",
        operation_description="Get all top-level categories with subcategories.",
        responses={200: TopLevelCategorySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        categories = TopLevelCategory.objects.select_related('parent').filter(
            parent__isnull=True
        )
        serializer = TopLevelCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubCategoryAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Categories'],
        operation_summary="Get all top-level categories with subcategories.",
        operation_description="Get all top-level categories with subcategories.",
        responses={200: TopLevelCategorySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(TopLevelCategory, id=kwargs.get('id'))

        categories = SubCategory.objects.select_related('parent').filter(
            parent=instance
        )
        serializer = SubCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetQuizChoicesView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_description="Retrieve available year choices and mode of study choices for quizzes",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successfully retrieved choices",
            )
        }
    )
    def get(self, request, *args, **kwargs):
        data = {
            "year_choices": [{"id": choice[0], "label": choice[1]} for choice in Quiz.YEAR_CHOICES],
            "mode_of_study_choices": [{"id": choice[0], "label": choice[1]} for choice in Quiz.MODE_OF_STUDY_CHOICES],
        }
        return Response(data, status=status.HTTP_200_OK)


class QuizListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Get a list of quizzes",
        operation_description="Retrieve a list of quizzes with pagination and filtering options. "
                              "Filters available: mode_of_study, year, category, sub_category, and top_level_category.",
        manual_parameters=[
            openapi.Parameter('mode_of_study', openapi.IN_QUERY, description="Filter by mode of study",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('year', openapi.IN_QUERY, description="Filter by year", type=openapi.TYPE_STRING),
            openapi.Parameter('field', openapi.IN_QUERY, description="Filter by field name", type=openapi.TYPE_STRING),
            openapi.Parameter('degree', openapi.IN_QUERY, description="Filter by degree name",
                              type=openapi.TYPE_STRING),
        ],
        responses={200: QuizSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        queryset = Quiz.objects.all().order_by('-id')

        mode_of_study = request.query_params.get('mode_of_study')
        if mode_of_study:
            queryset = queryset.filter(mode_of_study=mode_of_study)

        year = request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)

        sub_category = request.query_params.get('field')
        if sub_category:
            queryset = queryset.filter(category__slug=sub_category)

        top_level_category = request.query_params.get('degree')
        if top_level_category:
            queryset = queryset.filter(category__parent__slug=top_level_category)

        paginator = QuizPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = QuizSerializer(paginated_queryset, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class RandomQuizzesView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Retrieves a list of random quizzes for a given category, including associated questions.",
        operation_description="Retrieves a list of random quizzes for a given category, including associated questions.",
        responses={
            200: QuizSerializer(many=True),
            404: 'Question not found'
        },
        manual_parameters=[
            openapi.Parameter(
                'quiz_id',
                openapi.IN_PATH,
                description='ID of the quiz to filter quizzes by',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, quizz_id):
        quiz = get_object_or_404(Quiz, id=quizz_id)

        quiz_questions = QuizQuestion.objects.filter(quiz=quiz).order_by('id')[:5]

        if not quiz_questions.exists():
            return Response({"detail": "Quiz questions not found or no questions in this quiz."},
                            status=status.HTTP_404_NOT_FOUND)

        quiz_serializer = QuizSerializer(quiz, context={'request': request})
        questions_serializer = QuizQuestionSerializer(quiz_questions, many=True, context={'request': request})

        return Response({
            "quizz_details": quiz_serializer.data,
            "test_list": questions_serializer.data
        }, status=status.HTTP_200_OK)


class StartTestView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Start a quiz test",
        operation_description="Fetches 25 random questions for a specific quiz if the quiz has been ordered by the user.",
        manual_parameters=[
            openapi.Parameter(
                'quizz_id',
                openapi.IN_PATH,
                description="ID of the quiz to fetch questions for",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'start',
                openapi.IN_QUERY,
                description="Start the quiz test. Pass 'true' to begin the quiz.",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'next',
                openapi.IN_QUERY,
                description="Move to the next question. Pass 'true' to navigate forward.",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'back',
                openapi.IN_QUERY,
                description="Move to the previous question. Pass 'true' to navigate backward.",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'question_id',
                openapi.IN_QUERY,
                description="Question id to send back test",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=kwargs.get('quizz_id'))

        start = request.query_params.get('start', False)
        forward = request.query_params.get('next', False)
        backward = request.query_params.get('back', False)
        question_id = request.query_params.get('question_id', False)

        if OrderQuiz.objects.select_related('quiz').filter(quiz=quiz).exists():

            if start:
                return self.start(quiz, request)

            if forward:
                return self.forward(quiz, request)

            if backward and question_id:
                return self.backward(quiz, request, question_id)

        return Response(
            {"error": "You must purchase this quiz to access its questions."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def start(self, quiz, request):
        quiz_questions = QuizQuestion.objects.filter(quiz=quiz).order_by('?')[:1]

        serializer = QuizQuestionSerializer(quiz_questions, many=True, context={'request': request})
        serialized_data = serializer.data

        create_test_answers = UserTestAnswers.objects.create(
            author=request.user,
            quiz=quiz
        )

        for question in quiz_questions:
            create_test_answers_question = TestAnswerQuestion.objects.create(
                question=question,
                test_answer_quiz=create_test_answers
            )

        return Response({
            "quizz": quiz.title,
            "test_list": serialized_data
        }, status=status.HTTP_200_OK)

    def forward(self, quiz, request):
        quiz_questions = QuizQuestion.objects.filter(quiz=quiz).order_by('?')[:1]

        serializer = QuizQuestionSerializer(quiz_questions, many=True, context={'request': request})
        serialized_data = serializer.data

        instance = UserTestAnswers.objects.select_related('author').filter(
            author=request.user
        ).select_related('quiz').filter(
            quiz=quiz
        ).last()

        if TestAnswerQuestion.objects.filter(test_answer_quiz=instance).count() >= 25:
            return Response({"detail": "You have already answered 25 questions for this quiz."},
                            status=status.HTTP_400_BAD_REQUEST)

        for question in quiz_questions:
            create_test_answers_question = TestAnswerQuestion.objects.create(
                question=question,
                test_answer_quiz=instance
            )

        return Response({
            "quizz": quiz.title,
            "test_list": serialized_data
        }, status=status.HTTP_200_OK)

    def backward(self, quiz, request, question_id):
        instance = UserTestAnswers.objects.select_related('author', 'quiz').filter(
            author=request.user,
            quiz=quiz
        ).last()

        if not instance:
            return Response({"detail": "No test answer found."}, status=status.HTTP_404_NOT_FOUND)

        questions = TestAnswerQuestion.objects.filter(
            test_answer_quiz=instance,
        )

        question_ids = [str(question.question.id) for question in questions]

        if str(question_id) in question_ids:
            current_index = question_ids.index(str(question_id))
            if current_index > 0:
                previous_question_id = question_ids[current_index - 1]
                previous_question = questions.filter(question__id=int(previous_question_id)).first()
                get_question = get_object_or_404(QuizQuestion, id=previous_question.question.id)
                question_options = QuestionOption.objects.filter(question=get_question)
                serializer = QuizQuestionSerializer(get_question, context={'request': request})
                serialized_data = serializer.data
                get_true_answer = QuestionOption.objects.filter(
                    question=get_question, is_correct=True)
                true_answers = [{"id": option.id, "text": option.text} for option in get_true_answer]

                select_answer = []
                selected_answer = previous_question.selected_answer
                if selected_answer:
                    select_answer = [{"id": selected_answer.id, "text": selected_answer.text}]

                return Response({
                    "quizz": quiz.title,
                    "test_list": serialized_data,
                    "select_answer": select_answer,
                    "true_answer": true_answers,
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "quizz": quiz.title,
                    "test_list": []
                }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Question not found."}, status=status.HTTP_404_NOT_FOUND)


class CheckQuizView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Check if a Question with the given ID exists.",
        operation_description="Check if a Question with the given ID exists.",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Question exists", examples={"msg": "True"}
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Question does not exist", examples={"msg": "False"}
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                'option_id',
                openapi.IN_PATH,
                description='ID of the question to filter quizzes by',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = get_object_or_404(QuestionOption, id=kwargs.get('option_id'))

        instance = UserTestAnswers.objects.select_related('author', 'quiz').filter(
            author=request.user,
            quiz=queryset.question.quiz
        ).last()

        get_back_question = TestAnswerQuestion.objects.select_related('test_answer_quiz').filter(
            test_answer_quiz=instance,
            question=queryset.question
        ).last()

        if queryset.is_correct:
            get_back_question.selected_answer = queryset
            get_back_question.save()
            return Response({'msg': True}, status=status.HTTP_200_OK)

        get_true_answer = QuestionOption.objects.select_related('question').filter(
            question=queryset.question, is_correct=True
        )
        get_back_question.selected_answer = queryset
        get_back_question.save()
        true_answers = [{"id": option.id, "text": option.text} for option in get_true_answer]

        return Response({'msg': False, "true_answer": true_answers}, status=status.HTTP_200_OK)


class UploadTestFileView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Upload and process a test file",
        operation_description=(
                "This endpoint allows users to upload a test file for processing. "
                "The file is temporarily saved, processed, and deleted afterward. "
                "A success or error response is returned based on the processing result."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="The file to upload and process",
                required=True,
            ),
            openapi.Parameter(
                name="category_id",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                description="The category ID to associate with the test",
                required=True,
            )
        ],
        responses={
            201: openapi.Response(
                description="File processed successfully",
                examples={"application/json": {"message": "File processed successfully"}},
            ),
            400: openapi.Response(
                description="Error occurred",
                examples={"application/json": {"error": "No file provided"}},
            ),
        },
    )
    def post(self, request):
        file = request.FILES.get('file')
        category_id = request.data.get('category_id')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        if not category_id:
            return Response({'error': 'No category ID provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category_id = int(category_id)
            category = SubCategory.objects.get(id=category_id)
        except (ValueError, SubCategory.DoesNotExist):
            return Response({'error': 'Invalid or non-existent category ID'}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(file.name, file)
        full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if not default_storage.exists(file_path):
            return Response({'error': f"File not found: {file_path}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            import_tests_from_file(full_file_path, category)
            return Response({'message': 'File processed successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            default_storage.delete(file_path)


class FinishTestAuthor(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the latest test answers for the authenticated user.",
        operation_summary="Get User's Last Test Answers",
        responses={
            status.HTTP_200_OK: TestAnswerQuestionSerializer(many=True),
            status.HTTP_404_NOT_FOUND: openapi.Response(description="No test answers found.")
        },
        tags=['Quiz'],
    )
    def get(self, request):
        instance = UserTestAnswers.objects.select_related('author').filter(
            author=request.user
        ).last()
        count_true_answers = TestAnswerQuestion.objects.select_related('test_answer_quiz', 'selected_answer').filter(
            test_answer_quiz=instance, selected_answer__is_correct=True
        ).count()
        persentage_true_answers = (count_true_answers * 100) / 25
        responce_data = {
            'results': instance,
            'count_correct_answers': count_true_answers,
            'persentage_correct_answers': persentage_true_answers
        }
        serializer = TestResultSerializer(responce_data, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class BackQuestionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve detailed information about a specific test answer question.",
        operation_summary="Get Test Answer Question Details",
        manual_parameters=[
            openapi.Parameter(
                'quizz_id',
                openapi.IN_PATH,
                description="ID of the TestAnswerQuestion instance",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Successful retrieval of test answer question details.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the question"),
                        'question': openapi.Schema(type=openapi.TYPE_STRING, description="Question text"),
                        'test_answer_quiz': openapi.Schema(type=openapi.TYPE_INTEGER, description="Related quiz ID"),
                        'selected_answer': openapi.Schema(type=openapi.TYPE_INTEGER, description="Selected answer ID"),
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(description="TestAnswerQuestion not found.")
        },
        tags=['Quiz']
    )
    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(TestAnswerQuestion, id=kwargs.get('quizz_id'))

        serializer = TestAnswerQuestionSerializer(instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
