from django import forms
from .models import BorrowedBook
from catalog.models import Book
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class BorrowBookForm(forms.ModelForm):
    book = forms.ModelChoiceField(queryset=Book.objects.filter(available_copies__gt=0))

    class Meta:
        model = BorrowedBook
        fields = ['book']

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]