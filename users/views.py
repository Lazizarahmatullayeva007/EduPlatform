from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .forms import RegisterForm, ProfileForm
from .models import SMSVerification
from .eskiz_utils import send_sms
from .serializers import (
    SendVerificationCodeSerializer,
    VerifyPhoneSerializer,
    UserProfileSerializer,
)
import random


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}! Ro'yxatdan muvaffaqiyatli o'tdingiz.")
            return redirect('courses:course_list')
        else:
            messages.error(request, "Ro'yxatdan o'tishda xatolik yuz berdi. Ma'lumotlarni tekshirib qayta kiriting.")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})



@login_required
def profile(request):
    """
    Profilni ko'rish VA tahrirlash - bitta sahifada.
    GET - formani mavjud ma'lumotlar bilan to'ldirib ko'rsatadi.
    POST - o'zgarishlarni saqlaydi.
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil yangilandi")
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)

    stats = {}
    if request.user.role == 'student':
        stats['enrolled_count'] = request.user.enrollments.count()
        stats['completed_count'] = request.user.enrollments.filter(progress_percent__gte=100).count()
    else:
        stats['courses_count'] = request.user.courses.count()
        stats['total_students'] = sum(c.enrolled_count() for c in request.user.courses.all())

    return render(request, 'users/profile.html', {'form': form, 'stats': stats})


class SendVerificationCodeView(APIView):
    """
    Telefon raqamiga 6 xonali tasodifiy kod yaratib, SMS orqali yuboradi.
    Har kim (login qilmagan foydalanuvchi ham) chaqira oladi.
    """
    permission_classes = [AllowAny]
    serializer_class = SendVerificationCodeSerializer

    @extend_schema(
        tags=['Foydalanuvchilar (Auth & Verification)'],
        summary='Telefon raqamiga tasdiqlash kodi yuborish',
        request=SendVerificationCodeSerializer,
        responses={
            200: OpenApiResponse(description="SMS kod muvaffaqiyatli yuborildi"),
            400: OpenApiResponse(description="Xato parametrlar"),
        }
    )
    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone_number = serializer.validated_data['phone_number']
        code = str(random.randint(100000, 999999))
        SMSVerification.objects.create(phone_number=phone_number, code=code)

        send_sms(phone_number, f"EduPlatform tasdiqlash kodi: {code}")

        return Response({"message": "Kod yuborildi", "phone_number": phone_number})


class VerifyPhoneView(APIView):
    """
    Foydalanuvchi kiritgan kodni tekshiradi.
    Kod: to'g'ri bo'lishi, 5 daqiqadan eski bo'lmasligi, va oldin ishlatilmagan bo'lishi kerak.
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyPhoneSerializer

    @extend_schema(
        tags=['Foydalanuvchilar (Auth & Verification)'],
        summary='Telefon raqami SMS kodini tasdiqlash',
        request=VerifyPhoneSerializer,
        responses={
            200: OpenApiResponse(description="Telefon raqami tasdiqlandi"),
            400: OpenApiResponse(description="Kod noto'g'ri yoki muddati o'tgan"),
        }
    )
    def post(self, request):
        serializer = VerifyPhoneSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        five_minutes_ago = timezone.now() - timedelta(minutes=5)

        verification = SMSVerification.objects.filter(
            phone_number=phone_number,
            code=code,
            is_used=False,
            created_at__gte=five_minutes_ago,
        ).first()

        if not verification:
            return Response({"error": "Kod noto'g'ri yoki muddati o'tgan"}, status=400)

        verification.is_used = True
        verification.save()

        User = get_user_model()
        User.objects.filter(phone_number=phone_number).update(is_phone_verified=True)

        return Response({"message": "Telefon raqami tasdiqlandi", "phone_number": phone_number})


class UserProfileAPIView(APIView):
    """
    Joriy tizimga kirgan foydalanuvchining profil ma'lumotlarini olish va yangilash API.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    @extend_schema(
        tags=['Foydalanuvchilar (Auth & Verification)'],
        summary='Foydalanuvchi profil ma\'lumotlarini olish',
        responses={200: UserProfileSerializer}
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        tags=['Foydalanuvchilar (Auth & Verification)'],
        summary='Foydalanuvchi profil ma\'lumotlarini yangilash',
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)