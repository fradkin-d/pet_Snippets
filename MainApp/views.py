from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.db.models import Count

from .forms import SnippetForm
from .models import Snippet
from Comments.forms import CommentForm
from AJAX.models import SnippetLike


def index_page(request):
    context = {
        'pagename': '',
        'snippets_count': Snippet.objects.all().count(),
        'top_ten_by_rating': top_ten_by_rating(),
        'top_ten_by_reviews': top_ten_by_reviews()
    }
    return render(request, 'pages/index.html', context)


def top_ten_by_rating():
    return Snippet.objects.filter(is_private=False) \
               .annotate(likes=Count('snippetlike')) \
               .filter(likes__gt=0) \
               .order_by('-likes')[:10]


def top_ten_by_reviews():
    return Snippet.objects.filter(is_private=False) \
               .annotate(comments=Count('comment')) \
               .filter(comments__gt=0) \
               .order_by('-comments')[:10]


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


def snippet_delete(request, slug):
    Snippet.objects.filter(slug=slug, author=request.user).delete()
    messages.success(request, f'Сниппет удален')
    return redirect('my_snippets_list_page')


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
