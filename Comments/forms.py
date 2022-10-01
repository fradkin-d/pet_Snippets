from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    text = forms.CharField(label='Ваш комментарий', widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = Comment
        fields = ['text']
