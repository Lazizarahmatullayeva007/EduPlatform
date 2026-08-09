from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

INPUT_CLASSES = "w-full rounded-xl border border-slate-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['bio', 'avatar', 'phone_number']
        widgets = {
            'bio': forms.Textarea(attrs={'class': INPUT_CLASSES, 'rows': 4}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'mt-1'}),
            'phone_number': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': '+998...'}),
        }