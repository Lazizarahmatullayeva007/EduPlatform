from django import forms
from .models import Course, Comment

INPUT_CLASSES = "w-full border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'price', 'max_students', 'cover_image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 5}),
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'price': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'max_students': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'mt-1'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'w-5 h-5 accent-blue-600'}),
        }



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 3,
                'placeholder': 'Fikringizni yozing...'
            }),
        }