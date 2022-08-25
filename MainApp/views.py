from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import auth
from MainApp.forms import UserRegistrationForm, SnippetForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from .models import Snippet, Comment, SnippetLike


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
            return redirect(request.META.get('HTTP_REFERER', '/'))
    context = {
        'pagename': 'Добавление нового сниппета',
        'form': form
    }
    return render(request, 'pages/add_snippet.html', context)


class SnippetListView(ListView):
    model = Snippet
    template_name = 'pages/snippet_list.html'
    paginate_by = 32

    def get_queryset(self):
        """Not the best way, but was easy for me. Need to change in future"""
        return super().get_queryset().filter(is_private=False)

    def get_ordering(self):
        ordering = self.request.GET.get('sort')
        return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Список сниппетов'
        context['current_order'] = self.get_ordering()
        context['current_page'] = self.get_ordering()
        return context


class MySnippetListView(ListView):
    model = Snippet
    template_name = 'pages/my_snippet_list.html'
    paginate_by = 32

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_ordering(self):
        ordering = self.request.GET.get('sort')
        return ordering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Мои сниппеты'
        context['current_order'] = self.get_ordering()
        context['current_page'] = self.get_ordering()
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
    comment = Comment.objects.get(pk=pk)
    if comment.author == request.user:
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
