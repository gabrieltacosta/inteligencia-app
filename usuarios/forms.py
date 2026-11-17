from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuário',
        required=True,
        widget=forms.TextInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'placeholder': 'Digite seu usuário', 'aria-label': 'Usuário', "autofocus": "autofocus"}),
    )
    password = forms.CharField(
        label='Senha',
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500', 'placeholder': 'Digite sua senha', 'aria-label': 'Senha'}),
    )