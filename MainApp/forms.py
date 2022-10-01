import django.forms as forms
from MainApp.models import Snippet, SupportedLang


CODE_LANGS = [('', '')]+[(code_lang.lang,)*2 for code_lang in SupportedLang.objects.all()]


class SnippetForm(forms.ModelForm):
    name = forms.CharField(label='Имя')
    lang = forms.ModelChoiceField(queryset=SupportedLang.objects.all(), label='Язык', empty_label='')
    description = forms.CharField(label='Описание', max_length=250,
                                  widget=forms.Textarea(attrs={"rows": 4}),
                                  required=False)
    code = forms.CharField(label='Код', widget=forms.Textarea)
    is_private = forms.BooleanField(label='Приватный', required=False)

    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'description', 'code', 'is_private']




        