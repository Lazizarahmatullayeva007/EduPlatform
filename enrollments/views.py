from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
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

    if course.price > 0:
        messages.warning(request, "Bu kurs pullik. Yozilish uchun to'lovni amalga oshiring.")
        return redirect('enrollments:checkout', slug=slug)

    already_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()

    if already_enrolled:
        messages.info(request, "Siz allaqachon bu kursga yozilgansiz")
    else:
        if course.is_full():
            messages.error(request, "Ushbu kursda bo'sh o'rin qolmagan.")
            return redirect('courses:course_detail', slug=slug)
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, "Muvaffaqiyatli kursga yozildingiz! 1-dars ochildi.")

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

    transaction.atomic() - to'lov holatini yangilash VA kursga yozish
    bitta "bo'linmas" amal sifatida bajariladi. Agar ikkinchi qadam
    (Enrollment yaratish) muvaffaqiyatsiz bo'lsa, birinchi qadam
    (payment.save()) ham AVTOMATIK bekor qilinadi - shunday qilib
    "to'lov qilingan, lekin kursga yozilmagan" degan noto'g'ri holat
    hech qachon yuzaga kelmaydi.
    """
    if request.method != 'POST':
        return redirect('courses:course_list')

    payment = get_object_or_404(Payment, transaction_id=transaction_id, student=request.user)

    if payment.status != 'paid':
        with transaction.atomic():
            payment.status = 'paid'
            payment.paid_at = timezone.now()
            payment.save()
            Enrollment.objects.get_or_create(student=payment.student, course=payment.course)

    messages.success(request, f"To'lov muvaffaqiyatli! '{payment.course.title}' kursiga yozildingiz.")
    return redirect('courses:course_detail', slug=payment.course.slug)


from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from .serializers import EnrollmentSerializer, PaymentSerializer, InitiatePaymentResponseSerializer


class InitiatePaymentView(APIView):
    """
    DRF orqali JWT bilan ishlaydigan versiya (tashqi API mijozlar uchun,
    masalan mobil ilova). HTML sayt esa yuqoridagi checkout()ni ishlatadi.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = InitiatePaymentResponseSerializer

    @extend_schema(
        tags=['To\'lovlar va Yozilishlar'],
        summary='Kurs uchun to\'lov jarayonini boshlash (API)',
        responses={
            200: InitiatePaymentResponseSerializer,
            400: OpenApiResponse(description="Allaqachon yozilgan yoki xato kurs"),
        }
    )
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

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Noto'g'ri JSON format"}, status=400)

    transaction_id = data.get('transaction_id')
    received_signature = request.headers.get('X-Signature', '')
    secret_key = getattr(settings, 'PAYME_WEBHOOK_SECRET', 'eduplatform_payme_secret_key')

    expected_signature = hmac.new(
        secret_key.encode(),
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


@extend_schema_view(
    list=extend_schema(tags=['To\'lovlar va Yozilishlar'], summary='Foydalanuvchining yozilgan kurslari ro\'yxati'),
    retrieve=extend_schema(tags=['To\'lovlar va Yozilishlar'], summary='Yozilish tafsilotlari'),
    create=extend_schema(tags=['To\'lovlar va Yozilishlar'], summary='Kursga yozilish (API)'),
    destroy=extend_schema(tags=['To\'lovlar va Yozilishlar'], summary='Kursdan chiqish (yozilishni bekor qilish)'),
)
class MyEnrollmentsViewSet(viewsets.ModelViewSet):
    """Foydalanuvchi o'z kurslarini ko'radi va yangi kursga API orqali yoziladi."""
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, CourseNotFull]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


@extend_schema_view(
    list=extend_schema(tags=['To\'lovlar va Yozilishlar'], summary='Foydalanuvchining to\'lovlari tarixi'),
    retrieve=extend_schema(tags=['To\'lovlar va Yozilishlar'], summary='To\'lov tafsilotlari'),
)
class PaymentHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', '') == 'teacher':
            return Payment.objects.filter(course__teacher=user).select_related('student', 'course')
        return Payment.objects.filter(student=user).select_related('student', 'course')