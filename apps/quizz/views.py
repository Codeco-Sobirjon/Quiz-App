import random

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from apps.quizz.models import (
    SubCategory, TopLevelCategory, Category,
    Quiz, Question
)
import os
from django.conf import settings
from apps.quizz.serializers import TopLevelCategorySerializer, QuizSerializer
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


class RandomQuizzesView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Quiz'],
        operation_summary="Retrieves a list of random quizzes for a given category, including associated questions.",
        operation_description="Retrieves a list of random quizzes for a given category, including associated questions.",
        responses={
            200: QuizSerializer(many=True),
            404: 'Category not found or no quizzes in this category.'
        },
        manual_parameters=[
            openapi.Parameter(
                'category_id',
                openapi.IN_PATH,
                description='ID of the category to filter quizzes by',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, category_id):
        queryset = get_object_or_404(Category, id=category_id)
        try:
            quiz = Quiz.objects.select_related('category').filter(
                category=queryset
            ).order_by('?')[:4]
        except Quiz.DoesNotExist:
            return Response({"error": "Category not found or no quizzes in this category."}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizSerializer(quiz, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
        queryset = get_object_or_404(Question, id=kwargs.get('question_id'))
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