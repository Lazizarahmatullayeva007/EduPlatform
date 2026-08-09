from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'enrollments'

router = DefaultRouter()
router.register('api/my-courses', views.MyEnrollmentsViewSet, basename='my-enrollments')

urlpatterns = [
    path('enroll/<slug:slug>/', views.enroll_course, name='enroll_course'),
    path('unenroll/<slug:slug>/', views.unenroll_course, name='unenroll_course'),
    path('my-courses/', views.my_enrollments, name='my_enrollments'),
    path('checkout/<slug:slug>/', views.checkout, name='checkout'),
    path('simulate-pay/<uuid:transaction_id>/', views.simulate_payment_success, name='simulate_payment'),
    path('pay/<slug:slug>/', views.InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment-webhook/', views.payment_webhook, name='payment_webhook'),
    path('', include(router.urls)),
]