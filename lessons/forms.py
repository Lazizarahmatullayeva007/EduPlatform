from django import forms
from .models import Lesson

INPUT_CLASSES = (
    "w-full border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 "
    "bg-white dark:bg-slate-700/80 text-slate-800 dark:text-slate-100 "
    "placeholder-slate-400 dark:placeholder-slate-400 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
)



class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'lesson_type', 'video_url', 'video_file', 'text_content', 'order', 'duration_minutes']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'lesson_type': forms.Select(attrs={'class': INPUT_CLASSES}),
            'video_url': forms.URLInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'https://... (yoki pastdan fayl yuklang)'}),
            'video_file': forms.ClearableFileInput(attrs={'class': 'mt-1'}),
            'text_content': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 6}),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            'duration_minutes': forms.NumberInput(attrs={'class': INPUT_CLASSES,
                                                         'placeholder': "Fayl yuklasangiz avtomatik, YouTube link uchun qo'lda kiriting"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].required = False
        self.fields['duration_minutes'].required = False