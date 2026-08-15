from django.urls import path, include
from rest_framework.routers import DefaultRouter
from courses.views import CourseViewSet, CategoryViewSet, CommentViewSet
from lessons.views import LessonViewSet
from enrollments.views import MyEnrollmentsViewSet, PaymentHistoryViewSet, InitiatePaymentView
from users.views import SendVerificationCodeView, VerifyPhoneView, UserProfileAPIView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register('courses', CourseViewSet, basename='api-course')
router.register('categories', CategoryViewSet, basename='api-category')
router.register('comments', CommentViewSet, basename='api-comment')
router.register('lessons', LessonViewSet, basename='api-lesson')
router.register('my-courses', MyEnrollmentsViewSet, basename='api-my-enrollments')
router.register('payments', PaymentHistoryViewSet, basename='api-payment-history')

urlpatterns = [
    # DRF ViewSets (Root router /api/)
    path('', include(router.urls)),

    # Users & Auth APIs
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('profile/', UserProfileAPIView.as_view(), name='api_profile'),
    path('send-code/', SendVerificationCodeView.as_view(), name='api_send_code'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='api_verify_phone'),

    # Payment initiate
    path('pay/<slug:slug>/', InitiatePaymentView.as_view(), name='api_initiate_payment'),

    # OpenAPI Schema & Swagger Documentation
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='api_docs'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='api_swagger'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='api_redoc'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
