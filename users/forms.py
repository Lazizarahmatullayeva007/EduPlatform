from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

INPUT_CLASSES = (
    "w-full border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 "
    "bg-white dark:bg-slate-700/80 text-slate-800 dark:text-slate-100 "
    "placeholder-slate-400 dark:placeholder-slate-400 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
)



class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Foydalanuvchi nomi"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Parol"
        })
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Email"
        })
    )

    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={
            "class": INPUT_CLASSES
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Parol"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Parolni tasdiqlang"
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "Foydalanuvchi nomi"
            }),
        }


COMPACT_INPUT_CLASSES = (
    "w-full border border-slate-300 dark:border-slate-600 rounded-xl px-3.5 py-2 text-xs "
    "bg-white dark:bg-slate-700/80 text-slate-800 dark:text-slate-100 "
    "placeholder-slate-400 dark:placeholder-slate-400 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['bio', 'avatar', 'phone_number']
        widgets = {
            'bio': forms.Textarea(attrs={'class': COMPACT_INPUT_CLASSES, 'rows': 2, 'placeholder': 'O\'zingiz haqingizda kiritishingiz mumkin...'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'mt-1'}),
            'phone_number': forms.TextInput(attrs={'class': COMPACT_INPUT_CLASSES, 'placeholder': '+998...'}),
        }