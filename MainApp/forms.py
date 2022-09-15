from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import django.forms as forms
from MainApp.models import Snippet, Comment, SupportedLang


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', max_length=150)  # please, change max_length to 15!!!
    email = forms.EmailField(label='Адрес электронной почты')

    class Meta:
        model = User
        fields = ["username", "email"]

    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput)

    def clean_password2(self):
        pass1 = self.cleaned_data.get("password1")
        pass2 = self.cleaned_data.get("password2")
        if pass1 and pass2 and pass1 == pass2:
            return pass2
        raise ValidationError("Пароли не совпадают или пустые")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


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


class CommentForm(forms.ModelForm):
    text = forms.CharField(label='Ваш комментарий', widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        model = Comment
        fields = ['text']

        