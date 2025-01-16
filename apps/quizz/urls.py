from django.urls import path

from apps.quizz.views import TopLevelCategoryAPIView, RandomQuizzesView, CheckQuizView, UploadTestFileView, \
    SubCategoryAPIView, GetQuizChoicesView, QuizListView, StartTestView, FinishTestAuthor

urlpatterns = [
    path('degree/', TopLevelCategoryAPIView.as_view(), name='fileds'),
    path('field/<int:id>/', SubCategoryAPIView.as_view(), name='sub-fields'),
    path('quiz-choices/', GetQuizChoicesView.as_view(), name='get-quiz-choices'),
    path('all/', QuizListView.as_view(), name='quizs'),
    path('random-quizzes/<int:quiz_id>/', RandomQuizzesView.as_view(), name='random-quizzes'),
    path('start-test/<int:quiz_id>/', StartTestView.as_view(), name="start-test"),
    path('check-quiz/<int:option_id>/', CheckQuizView.as_view(), name='check-quiz'),
    path('finish-quiz/', FinishTestAuthor.as_view(), name='finish-quiz'),
]
