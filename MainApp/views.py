from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import auth, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.db.models import Count
from django.http import JsonResponse
import math
from MainApp.forms import UserRegistrationForm, SnippetForm, CommentForm
from .models import Snippet, Comment, SnippetLike
from django.db import connection


def index_page(request):
    context = {
        'pagename': '',
        'snippets_count': Snippet.objects.all().count(),
        'top_ten_by_rating': top_ten_by_rating(),
        'top_ten_by_reviews': top_ten_by_reviews()
    }
    return render(request, 'pages/index.html', context)


def top_ten_by_rating():
    """
    Returns top-10 snippets by rating
    """
    return Snippet.objects.filter(is_private=False).annotate(likes=Count('snippetlike')).filter(likes__gt=0).order_by('-likes')[:10]


def top_ten_by_reviews():
    """
    Returns top-10 snippets by reviews
    """
    return Snippet.objects.filter(is_private=False).annotate(comments=Count('comment')).filter(comments__gt=0).order_by('-comments')[:10]


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


class SnippetCreateView(SuccessMessageMixin, CreateView):
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/add_snippet.html'
    success_url = reverse_lazy('my_snippets_list_page')
    success_message = "Сниппет добавлен"

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('snippet_detail_page', args=(self.object.slug,))


class SnippetUpdateView(SuccessMessageMixin, UpdateView):
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/snippet_update.html'
    success_message = "Сниппет обновлен"

    def get_success_url(self):
        return self.request.GET.get('next')


class SnippetDeleteView(SuccessMessageMixin, DeleteView):
    model = Snippet
    success_url = reverse_lazy('my_snippets_list_page')
    template_name = 'pages/snippet_delete.html'
    success_message = "Сниппет удален"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Удаление сниппета'
        context['back_page'] = self.request.META.get('HTTP_REFERER', '/')
        return context


class SnippetDetailView(DetailView):
    model = Snippet
    template_name = 'pages/snippet_detail.html'
    context_object_name = 'snippet'

    def dispatch(self, request, *args, **kwargs):
        _object = self.get_object()
        _user = self.request.user
        if _object.is_private is True and _object.author != _user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Просмотр сниппета'
        context['user'] = self.request.user
        context['comment_form'] = CommentForm
        if self.request.user.id is not None:
            context['is_liked'] = SnippetLike.objects.filter(snippet=self.object, author=self.request.user).exists()
            context['anon_user'] = False
        else:
            context['anon_user'] = True
        return context


def snippets_list(request):
    context = {'pagename': 'База сниппетов'}
    return render(request, 'pages/snippet_list.html', context)


def user_snippets_list(request):
    context = {'pagename': 'Мои сниппеты'}
    return render(request, 'pages/my_snippet_list.html', context)


def snippets_json(request, username=''):
    search = request.GET.get('search[value]')
    order_i = request.GET.get('order[0][column]')
    order_col = request.GET.get(f'columns[{order_i}][data]')
    order_dir = request.GET.get('order[0][dir]')
    start = request.GET.get('start')
    length = request.GET.get('length')

    sql = f'''WITH vars(search_var) AS (values('{search if search else ""}%')) SELECT s.name AS name, s.lang_id AS lang, COUNT(DISTINCT sl.id) AS like_count, COUNT(DISTINCT c.id) AS comment_count, {"s.is_private AS is_private" if username else "u.username AS author"}, s.creation_date AS creation_date, s.slug AS slug FROM "MainApp_snippet" AS s LEFT OUTER JOIN "MainApp_comment" AS c ON s.id = c.snippet_id LEFT OUTER JOIN "MainApp_snippetlike" AS sl ON s.id = sl.snippet_id LEFT OUTER JOIN "auth_user" AS u ON s.author_id = u.id, vars {f"WHERE u.username = '{username}'" if username else "WHERE s.is_private = FALSE"} GROUP BY s.id, u.username, vars.search_var HAVING s."name" LIKE vars.search_var OR s.lang_id  LIKE vars.search_var OR u.username LIKE vars.search_var ORDER BY {order_col if order_col else 'creation_date'} {order_dir if order_dir else 'desc'}'''

    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        data = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    response = {
        'data': data,
        'recordsTotal': Snippet.objects.all().count(),
        'recordsFiltered': len(data)
    }

    if start and length:
        response.update({
            'data': data[int(start):int(start) + int(length)],
            'page': math.ceil(int(start) / int(length)) + 1,
            'per_page': int(length),
        })
    # pp(connection.queries)
    return JsonResponse(response)


def snippet_json_non_private(request):
    return snippets_json(request)


@login_required
def snippet_json_user_is_author(request):
    return snippets_json(request, request.user.username)


@login_required(redirect_field_name=None)
def create_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        form.instance.author = request.user
        form.instance.snippet = Snippet.objects.get(pk=request.POST.get('snippet'))
        if form.is_valid():
            form.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_comment(request, pk):
    Comment.objects.get(pk=pk, author=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def switch_snippetlike(request, snippet_id):
    snippet = Snippet.objects.get(pk=snippet_id)
    response = {
        'was_liked': SnippetLike.objects.filter(snippet=snippet, author=request.user).exists()
    }
    if response['was_liked']:
        SnippetLike.objects.filter(snippet=snippet, author=request.user).delete()
    else:
        SnippetLike.objects.create(snippet=snippet, author=request.user)
    return JsonResponse(response)
