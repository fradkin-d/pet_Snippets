from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import auth
from MainApp.forms import UserRegistrationForm, SnippetForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from .models import Snippet, Comment, SnippetLike, SupportedLang
from django.db.models import Count, Sum


def index_page(request):
    context = {'pagename': 'Snippets'}
    return render(request, 'pages/index.html', context)


def registration(request):
    form = UserRegistrationForm
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            form.save()
            # return Success message
            return redirect('home')
        # return Error message
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
            # return Success message
        else:
            # return Error message
            pass
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def logout(request):
    auth.logout(request)
    return redirect('home')


@login_required
def add_snippet_page(request):
    form = SnippetForm
    if request.method == 'POST':
        form = form(request.POST)
        form.instance.author = request.user
        if form.is_valid():
            form.save()
            # return Success message
            return redirect('my_snippets_list_page')
    context = {
        'pagename': 'Добавление нового сниппета',
        'form': form
    }
    return render(request, 'pages/add_snippet.html', context)


class SnippetUpdateView(UpdateView):
    model = Snippet
    fields = [
        "name",
        "lang",
        "is_private",
        "code",
    ]
    template_name = 'pages/snippet_update.html'
    success_url = reverse_lazy('my_snippets_list_page')


class SnippetDeleteView(DeleteView):
    model = Snippet
    success_url = reverse_lazy('my_snippets_list_page')
    template_name = 'pages/snippet_delete.html'

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
        context['is_liked'] = SnippetLike.objects.filter(snippet=self.object, author=self.request.user).exists()
        return context


class SnippetListView(ListView):
    model = Snippet
    template_name = 'pages/snippet_list.html'
    paginate_by = 4
    filter_date_from = ''
    filter_date_to = ''
    filter_lang = 'all'
    filter_author = 'all'
    queryset = Snippet.objects.all().annotate(
        comment_count=Count('comment'),
        like_count=Sum('snippetlike')
    )

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_private=False)

        # filter date from
        self.filter_date_from = self.request.GET.get('date_from')
        if self.filter_date_from is not None and self.filter_date_from not in ['', 'None']:
            queryset = queryset.filter(creation_date__gte=self.filter_date_from)

        # filter date to
        self.filter_date_to = self.request.GET.get('date_to')
        if self.filter_date_to is not None and self.filter_date_to not in ['', 'None']:
            queryset = queryset.filter(creation_date__lte=self.filter_date_to)

        # filter lang
        self.filter_lang = self.request.GET.get('lang')
        if self.filter_lang not in ['all', 'None'] and self.filter_lang is not None:
            queryset = queryset.filter(lang=self.filter_lang)

        # filter author
        self.filter_author = self.request.GET.get('author')
        if self.filter_author not in ['all', 'None'] and self.filter_author is not None:
            author = User.objects.get(username=self.filter_author)
            queryset = queryset.filter(author=author)

        return queryset

    def get_ordering(self):
        ordering = self.request.GET.get('sort')
        return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Список сниппетов'
        context['current_order'] = context['current_page'] = self.get_ordering()
        context['filter_date_from'] = self.filter_date_from
        context['filter_date_to'] = self.filter_date_to
        context['filter_lang'] = self.filter_lang
        context['filter_author'] = self.filter_author
        context['langs'] = [supported_lang.lang for supported_lang in SupportedLang.objects.all()]
        context['authors'] = [user.username for user in User.objects.all()]
        return context


class MySnippetListView(SnippetListView):
    template_name = 'pages/my_snippet_list.html'

    def get_queryset(self):
        return super(SnippetListView, self).get_queryset().filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Мои сниппеты'
        return context


def create_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        form.instance.author = request.user
        form.instance.snippet = Snippet.objects.get(pk=request.POST.get('snippet'))
        if form.is_valid():
            form.save()
            # return Success message
    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_comment(request, pk):
    comment = Comment.objects.get(pk=pk, author=request.user)
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def create_snippetlike(request, snippet_id):
    snippet = Snippet.objects.get(pk=snippet_id)
    user = request.user
    if not SnippetLike.objects.filter(snippet=snippet, author=user).exists():
        like = SnippetLike(snippet=snippet, author=user)
        like.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def delete_snippetlike(request, snippet_id):
    snippet = Snippet.objects.get(pk=snippet_id)
    snippetlike = SnippetLike.objects.filter(snippet=snippet, author=request.user)
    snippetlike.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))
