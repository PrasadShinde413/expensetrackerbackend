from django.urls import path
from .views import *

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('login/', LoginView.as_view()),
    
    # Business Logic
    path('users/<int:user_id>/categories/', CategoryView.as_view()),
    path('users/<int:user_id>/transactions/', TransactionView.as_view()),
    path('users/<int:user_id>/transactions/<int:pk>/', TransactionDetailView.as_view()),
    path('users/<int:user_id>/categories/<int:pk>/', CategoryDetailView.as_view()),
    path('users/<int:user_id>/dashboard/', DashboardView.as_view()),
    path('users/<int:user_id>/reports/', ReportView.as_view()),
]