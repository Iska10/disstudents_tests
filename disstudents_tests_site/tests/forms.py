from django import forms
from django.forms import PasswordInput


# форма авторизации
class LoginForm(forms.Form):
    username = forms.CharField(max_length=10, required=True, label='Логин')
    password = forms.CharField(widget=PasswordInput(), required=True, label='Пароль')
