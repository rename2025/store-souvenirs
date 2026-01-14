from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms

User = get_user_model()


from django.contrib.auth.forms import UserCreationForm


class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label='Имя', required=False)
    last_name = forms.CharField(max_length=50, label='Фамилия', required=False)
    email = forms.EmailField(label='Email', required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'


def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)  # UserCreationForm уже имеет password1/password2
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('products:home')
    else:
        form = RegisterUserForm()

    return render(request, 'users/register.html', {'form': form})


# Логин с AuthenticationForm
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('products:home')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form, 'error': form.errors})


def user_logout(request):
    logout(request)
    return redirect('products:home')


def profile(request):
    return render(request, 'users/profile.html')


def order_history(request):
    orders = []
    return render(request, 'users/orders.html', {'orders': orders})
