from django.urls import path

from apps.quizz.views import TopLevelCategoryAPIView, RandomQuizzesView, CheckQuizView, UploadTestFileView

urlpatterns = [
    path('top-level-categories/', TopLevelCategoryAPIView.as_view(), name='top-level-categories'),
    path('random-quizzes/<int:category_id>/', RandomQuizzesView.as_view(), name='random-quizzes'),
    path('check-quiz/<int:question_id>/', CheckQuizView.as_view(), name='checkl-quiz'),
    path('add-quiz/', UploadTestFileView.as_view(), name='add-quiz')
]
