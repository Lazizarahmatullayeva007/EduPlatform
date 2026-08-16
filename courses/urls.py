from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'courses'

router = DefaultRouter()
router.register('api/courses', views.CourseViewSet, basename='course-api')
router.register('api/categories', views.CategoryViewSet, basename='category-api')
router.register('api/comments', views.CommentViewSet, basename='comment-api')

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.course_create, name='course_create'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('', include(router.urls)),
    path('<slug:slug>/delete/', views.course_delete, name='course_delete'),
    path('<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('<slug:slug>/students/', views.course_students, name='course_students'),
    path('<slug:slug>/toggle-publish/', views.toggle_publish, name='toggle_publish'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
]