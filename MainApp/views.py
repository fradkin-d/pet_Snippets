from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import auth
from MainApp.forms import UserRegistrationForm, SnippetForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from .models import Snippet, Comment, SnippetLike, SupportedLang
from django.db.models import Count, Sum
from django.http import JsonResponse


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


class SnippetCreateView(CreateView):
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/add_snippet.html'
    success_url = reverse_lazy('my_snippets_list_page')

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        return super().form_valid(form)


class SnippetUpdateView(UpdateView):
    model = Snippet
    form_class = SnippetForm
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
        if self.request.user.id is not None:
            context['is_liked'] = SnippetLike.objects.filter(snippet=self.object, author=self.request.user).exists()
            context['anon_user'] = False
        else:
            context['anon_user'] = True
        return context


class SnippetListView(ListView):
    model = Snippet
    template_name = 'pages/snippet_list.html'
    queryset = Snippet.objects.all().annotate(
        comment_count=Count('comment'),
        like_count=Sum('snippetlike')
    )

    def get_queryset(self):
        return self.model.objects.all().filter(is_private=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'База сниппетов'
        return context


class MySnippetListView(SnippetListView):
    template_name = 'pages/my_snippet_list.html'

    def get_queryset(self):
        return self.model.objects.all().filter(author=self.request.user)

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


def model_objects_json(model):
    objects = model.objects.all()
    data = [obj.to_dict_json() for obj in objects]
    response = {
        'data': data
    }
    return JsonResponse(response)
