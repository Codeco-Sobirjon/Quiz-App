from django.urls import path

from apps.quizz.views import TopLevelCategoryAPIView, RandomQuizzesView, CheckQuizView, UploadTestFileView, \
    SubCategoryAPIView, GetQuizChoicesView, QuizListView

urlpatterns = [
    path('fileds/', TopLevelCategoryAPIView.as_view(), name='fileds'),
    path('sub-fields/<int:id>/', SubCategoryAPIView.as_view(), name='sub-fields'),
    path('quiz-choices/', GetQuizChoicesView.as_view(), name='get-quiz-choices'),
    path('all/', QuizListView.as_view(), name='quizs'),
    path('random-quizzes/<int:quiz_id>/', RandomQuizzesView.as_view(), name='random-quizzes'),

    # path('check-quiz/<int:question_id>/', CheckQuizView.as_view(), name='checkl-quiz'),
    # path('add-quiz/', UploadTestFileView.as_view(), name='add-quiz')
]
