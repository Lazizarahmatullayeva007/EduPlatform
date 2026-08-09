from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('send-code/', views.SendVerificationCodeView.as_view(), name='send_code'),
    path('verify-phone/', views.VerifyPhoneView.as_view(), name='verify_phone'),
]