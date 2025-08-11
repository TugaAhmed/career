from django.urls import path
from .views import SignupView, VerifyEmailView , LoginView , ActivateUserView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('activate/<uuid:uid>/<str:token>/', ActivateUserView.as_view(), name='activate-user'),
]


# # users/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('signup/', views.SignupView.as_view(), name='signup'),
#     path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
#     path('login/', views.LoginView.as_view(), name='login'),
# ]
