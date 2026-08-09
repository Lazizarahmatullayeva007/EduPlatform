from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'lessons'

router = DefaultRouter()
router.register('api/lessons', views.LessonViewSet, basename='lesson-api')

urlpatterns = [
    path('<slug:course_slug>/create/', views.lesson_create, name='lesson_create'),
    path('<slug:course_slug>/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
    path('<slug:course_slug>/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('', include(router.urls)),
]