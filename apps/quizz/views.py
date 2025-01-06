import random

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.quizz.models import (
    SubCategory, TopLevelCategory, Category,
    Quiz, Question
)
from apps.quizz.serializers import TopLevelCategorySerializer, QuizSerializer


class TopLevelCategoryAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Categories'],
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
