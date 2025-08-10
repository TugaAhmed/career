from django.urls import path
from .views import SignupView, VerifyEmailView , LoginView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
]


# # users/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('signup/', views.SignupView.as_view(), name='signup'),
#     path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
#     path('login/', views.LoginView.as_view(), name='login'),
# ]
