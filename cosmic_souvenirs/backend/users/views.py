from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = []

        if password1 != password2:
            errors.append('Пароли не совпадают')

        if User.objects.filter(username=username).exists():
            errors.append('Пользователь с таким именем уже существует')

        if len(password1) < 8:
            errors.append('Пароль должен быть не менее 8 символов')

        if errors:
            return render(request, 'users/register.html', {'errors': errors})

        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        return redirect('products:home')

    return render(request, 'users/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('products:home')
        else:
            return render(request, 'users/login.html', {'error': 'Неверный логин или пароль'})

    return render(request, 'users/login.html')


def user_logout(request):
    logout(request)
    return redirect('products:home')


def profile(request):
    return render(request, 'users/profile.html')


def order_history(request):
    orders = []
    return render(request, 'users/orders.html', {'orders': orders})