from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models import Course
from .models import Enrollment, Payment
from .serializers import EnrollmentSerializer
from .permissions import CourseNotFull
import json
import hmac
import hashlib


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

    already_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    if already_enrolled:
        messages.error(request, "Siz allaqachon bu kursga yozilgansiz")
    else:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, "Muvaffaqiyatli kursga yozildingiz!")

    return redirect('courses:course_detail', slug=slug)


@login_required
def my_enrollments(request):
    """
    Talaba o'zi yozilgan barcha kurslarni ko'radigan sahifa.
    """
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    return render(request, 'enrollments/my_enrollments.html', {'enrollments': enrollments})


@login_required
def unenroll_course(request, slug):
    """
    Talaba xato bosib yozilgan bo'lsa, kursdan chiqib ketishi uchun.
    """
    course = get_object_or_404(Course, slug=slug)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()

    if enrollment:
        enrollment.delete()
        messages.success(request, f"'{course.title}' kursidan chiqdingiz")
    else:
        messages.error(request, "Siz bu kursga yozilmagansiz")

    return redirect('enrollments:my_enrollments')


@login_required
def checkout(request, slug):
    """
    Talaba 'To'lash' tugmasini bosganda ochiladigan sahifa.
    Sessiya (login) orqali ishlaydi - JWT talab qilmaydi,
    chunki bu HTML sayt qismi, alohida API mijozi emas.
    """
    course = get_object_or_404(Course, slug=slug, is_published=True)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, "Siz allaqachon bu kursga yozilgansiz")
        return redirect('courses:course_detail', slug=slug)

    payment, created = Payment.objects.get_or_create(
        student=request.user,
        course=course,
        status='pending',
        defaults={'amount': course.price},
    )

    return render(request, 'enrollments/checkout.html', {'course': course, 'payment': payment})


@login_required
def simulate_payment_success(request, transaction_id):
    """
    HAQIQIY loyihada bu funksiya BO'LMAYDI - buning o'rniga
    talaba Payme sahifasida to'laydi, Payme esa payment_webhook'ga
    xabar yuboradi. Bu - faqat OQIMNI KO'RSATISH uchun simulyatsiya.
    """
    if request.method != 'POST':
        return redirect('courses:course_list')

    payment = get_object_or_404(Payment, transaction_id=transaction_id, student=request.user)

    if payment.status != 'paid':
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.save()
        Enrollment.objects.get_or_create(student=payment.student, course=payment.course)

    messages.success(request, f"To'lov muvaffaqiyatli! '{payment.course.title}' kursiga yozildingiz.")
    return redirect('courses:course_detail', slug=payment.course.slug)


class InitiatePaymentView(APIView):
    """
    DRF orqali JWT bilan ishlaydigan versiya (tashqi API mijozlar uchun,
    masalan mobil ilova). HTML sayt esa yuqoridagi checkout()ni ishlatadi.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({"error": "Siz allaqachon bu kursga yozilgansiz"}, status=400)

        payment = Payment.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            status='pending',
        )

        return Response({
            "transaction_id": str(payment.transaction_id),
            "amount": str(payment.amount),
            "message": "To'lov yaratildi. Haqiqiy loyihada bu yerda Payme to'lov linki qaytariladi.",
        })


@csrf_exempt
def payment_webhook(request):
    """
    Bu endpoint'ni TALABA emas, PAYME chaqiradi.
    Xavfsizlik uchun - so'rov PAYME_WEBHOOK_SECRET orqali
    hisoblangan imzo (signature) bilan kelishi SHART.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Faqat POST so'rov qabul qilinadi"}, status=405)

    data = json.loads(request.body)
    transaction_id = data.get('transaction_id')
    received_signature = request.headers.get('X-Signature', '')

    expected_signature = hmac.new(
        settings.PAYME_WEBHOOK_SECRET.encode(),
        str(transaction_id).encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(received_signature, expected_signature):
        return JsonResponse({"error": "Imzo noto'g'ri - bu so'rov Payme'dan emas"}, status=403)

    payment = get_object_or_404(Payment, transaction_id=transaction_id)

    if payment.status == 'paid':
        return JsonResponse({"message": "Bu to'lov allaqachon tasdiqlangan"})

    payment.status = 'paid'
    payment.paid_at = timezone.now()
    payment.save()

    Enrollment.objects.get_or_create(student=payment.student, course=payment.course)

    return JsonResponse({"message": "To'lov tasdiqlandi, talaba kursga yozildi"})


class MyEnrollmentsViewSet(viewsets.ModelViewSet):
    """Foydalanuvchi o'z kurslarini ko'radi va yangi kursga API orqali yoziladi."""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, CourseNotFull]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)