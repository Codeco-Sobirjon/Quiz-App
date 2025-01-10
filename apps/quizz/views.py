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
    Quiz, QuestionOption, QuizQuestion, OrderQuiz
)
import os
from django.conf import settings

from apps.quizz.pagination import QuizPagination
from apps.quizz.serializers import TopLevelCategorySerializer, QuizSerializer, SubCategorySerializer, \
    QuizQuestionSerializer
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
            openapi.Parameter('mode_of_study', openapi.IN_QUERY, description="Filter by mode of study", type=openapi.TYPE_STRING),
            openapi.Parameter('year', openapi.IN_QUERY, description="Filter by year", type=openapi.TYPE_STRING),
            openapi.Parameter('field', openapi.IN_QUERY, description="Filter by field name", type=openapi.TYPE_STRING),
            openapi.Parameter('degree', openapi.IN_QUERY, description="Filter by degree name", type=openapi.TYPE_STRING),
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
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)

        if request.user.is_authenticated:
            quiz_questions = QuizQuestion.objects.filter(quiz=quiz).order_by('id')[:5]
        else:
            quiz_questions = QuizQuestion.objects.filter(quiz=quiz).order_by('id')[:5]

        if not quiz_questions:
            return Response({"detail": "Quiz questions not found or no questions in this quiz."}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizQuestionSerializer(quiz_questions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class StartTestView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Start a quiz test",
        operation_description="Fetches 25 random questions for a specific quiz if the quiz has been ordered by the user.",
        manual_parameters=[
            openapi.Parameter(
                'quiz_id',
                openapi.IN_PATH,
                description="ID of the quiz to fetch questions for",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=kwargs.get('quiz_id'))

        if OrderQuiz.objects.select_related('quiz').filter(quiz=quiz).exists():
            quiz_questions = QuizQuestion.objects.filter(quiz=quiz).order_by('?')[:25]

            serializer = QuizQuestionSerializer(quiz_questions, many=True, context={'request': request})
            serialized_data = serializer.data

            return Response({
                "quizz": quiz.title,
                "test_list": serialized_data
            }, status=status.HTTP_200_OK)

        return Response(
            {"error": "You must purchase this quiz to access its questions."},
            status=status.HTTP_400_BAD_REQUEST
        )


class CheckQuizView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Check if a Question with the given ID exists.",
        operation_description="Check if a Question with the given ID exists.",
        responses={
            status.HTTP_200_OK: openapi.Response(description="Question exists", examples={"msg": "True"}),
            status.HTTP_404_NOT_FOUND: openapi.Response(description="Question does not exist",
                                                        examples={"msg": "False"})
        },

        manual_parameters = [
            openapi.Parameter(
                'question_id',
                openapi.IN_PATH,
                description='ID of the question to filter quizzes by',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        queryset = get_object_or_404(QuestionOption, id=kwargs.get('question_id'))
        if queryset.is_correct:
            return Response({'msg': True}, status=status.HTTP_200_OK)
        return Response({'msg': False}, status=status.HTTP_400_BAD_REQUEST)


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