from django.shortcuts import render, redirect
from django.contrib import auth
from MainApp.forms import UserRegistrationForm


def index_page(request):
    context = {'pagename': 'Snippets'}
    return render(request, 'pages/index.html', context)


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        print('1'*50)
        if form.is_valid():
            print('2'*50)
            form.save()
            print('3'*50)
            return redirect('home')
    context = {
        'pagename': 'Регистрация',
        'form': UserRegistrationForm,
    }
    return render(request, 'pages/registration.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
        else:
            # return Error message
            pass
        return redirect(request.META.get('HTTP_REFERER', '/'))


def logout(request):
    auth.logout(request)
    return redirect('home')


def add_snippet_page(request):
    context = {'pagename': 'Добавление нового сниппета'}
    return render(request, 'pages/add_snippet.html', context)


def snippets_list_page(request):
    context = {'pagename': 'Просмотр сниппетов'}
    return render(request, 'pages/view_snippets.html', context)
