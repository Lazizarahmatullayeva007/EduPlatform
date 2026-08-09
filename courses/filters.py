import django_filters
from .models import Course


class CourseFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    teacher = django_filters.CharFilter(field_name='teacher__username', lookup_expr='iexact')

    class Meta:
        model = Course
        fields = ['category', 'teacher', 'min_price', 'max_price']