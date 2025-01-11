from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshSlidingView

from apps.account.views import *

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('signin/', CustomAuthTokenView.as_view(), name='signin'),
    path('user/', CustomUserDetailView.as_view(), name='user-detail'),
    path('update-password/', PasswordUpdateView.as_view(), name='update-password'),
    path('token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),


]