from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from MainApp.models import Snippet
from .forms import CommentForm
from .models import Comment


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
