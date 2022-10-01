from django.contrib import messages, auth
from django.shortcuts import render, redirect

from .forms import UserRegistrationForm


def registration(request):
    form = UserRegistrationForm
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно!')
            new_user = auth.authenticate(username=form.cleaned_data['username'],
                                         password=form.cleaned_data['password1'])
            auth.login(request, new_user)
            messages.success(request, f'Добро пожаловать, {new_user.username}!')
            return redirect('home')
        messages.error(request, 'Ошибка регистрации! Проверьте правильность заполнения формы')
    context = {
        'pagename': 'Регистрация',
        'form': form,
    }
    return render(request, 'pages/registration.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url, '/')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка входа! Проверьте правильность заполнения формы')
    return render(request, 'pages/login.html', {'pagename': 'Вход'})


def logout(request):
    auth.logout(request)
    messages.success(request, f'Выполнен выход')
    return redirect('home')
