from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import auth, messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.db.models import Count, Q
from django.http import JsonResponse
import math
from MainApp.forms import UserRegistrationForm, SnippetForm, CommentForm
from .models import Snippet, Comment, SnippetLike


def index_page(request):
    context = {
        'pagename': 'Snippets',
        'snippets_count': Snippet.objects.all().count(),
        'top_ten_by_rating': top_ten_by_rating(),
        'top_ten_by_reviews': top_ten_by_reviews()
    }
    return render(request, 'pages/index.html', context)


def top_ten_by_rating():
    """
    Returns top-10 snippets by rating
    """
    return Snippet.objects.annotate(likes=Count('snippetlike')).filter(likes__gt=0).order_by('-likes')[:10]


def top_ten_by_reviews():
    """
    Returns top-10 snippets by reviews
    """
    return Snippet.objects.annotate(comments=Count('comment')).filter(comments__gt=0).order_by('-comments')[:10]


def registration(request):
    form = UserRegistrationForm
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно!')
            print(form)
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


class SnippetUpdateView(SuccessMessageMixin, UpdateView):
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/snippet_update.html'
    success_url = reverse_lazy('my_snippets_list_page')
    success_message = "Сниппет обновлен"


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


def snippet_json(request, snippets):
    """
    This function return JsonResponse with set of snippets and other info for datatable
    require snippets queryset as 'snippets' parameter
    """
    total = snippets.count()

    search = request.GET.get('search[value]')
    if search:
        snippets = snippets.filter(
            Q(name__icontains=search) |
            Q(lang__pk__icontains=search) |
            Q(author__username__icontains=search)
        )

    order_i = request.GET.get('order[0][column]')
    order_col = request.GET.get(f'columns[{order_i}][data]')
    order_dir = request.GET.get('order[0][dir]')
    if order_i:
        snippets = snippets.annotate(like_count=Count('snippetlike', distinct=True),
                                     comment_count=Count('comment', distinct=True)) \
            .order_by(f'{"-" if order_dir == "asc" else ""}{order_col}')
    _start = request.GET.get('start')
    _length = request.GET.get('length')

    data = [snippet.to_dict_json() for snippet in snippets]

    response = {
        'data': data,
        'recordsTotal': total,
        'recordsFiltered': total,
    }

    if _start and _length:
        start = int(_start)
        length = int(_length)
        page = math.ceil(start / length) + 1
        per_page = length

        response.update(
            {
                'data': data[start:start + length],
                'page': page,  # [opcional]
                'per_page': per_page,  # [opcional]
            }
        )
    return JsonResponse(response)


def snippet_json_non_private(request):
    """
    This function call snippet_json function with non-private snippets queryset as parameter
    """
    return snippet_json(request, Snippet.objects.filter(is_private=False))


@login_required
def snippet_json_user_is_author(request):
    """
    This function call snippet_json function with user's snippets queryset as parameter
    """
    return snippet_json(request, Snippet.objects.filter(author=request.user))


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
        SnippetLike(snippet=snippet, author=request.user).save()
    return JsonResponse(response)
