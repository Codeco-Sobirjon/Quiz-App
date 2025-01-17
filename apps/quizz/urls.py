from django.urls import path

from apps.quizz.views import TopLevelCategoryAPIView, RandomQuizzesView, CheckQuizView, UploadTestFileView, \
    SubCategoryAPIView, GetQuizChoicesView, QuizListView, StartTestView, FinishTestAuthor, BackQuestionDetailView

urlpatterns = [
    path('degree/', TopLevelCategoryAPIView.as_view(), name='fileds'),
    path('field/<int:id>/', SubCategoryAPIView.as_view(), name='sub-fields'),
    path('quizz-choices/', GetQuizChoicesView.as_view(), name='get-quiz-choices'),
    path('all/', QuizListView.as_view(), name='quizs'),
    path('random-quizzes/<int:quizz_id>/', RandomQuizzesView.as_view(), name='random-quizzes'),
    path('start-test/<int:quizz_id>/', StartTestView.as_view(), name="start-test"),
    path('check-quizz/<int:option_id>/', CheckQuizView.as_view(), name='check-quiz'),
    path('get-quizz-details/', FinishTestAuthor.as_view(), name='finish-quiz'),
    path('quiz/question/<int:quizz_id>/', BackQuestionDetailView.as_view(), name='question-detail'),
]
