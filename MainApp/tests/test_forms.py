from django.test import TestCase
from MainApp.forms import UserRegistrationForm, SnippetForm, CommentForm


class UserRegistrationFormTest(TestCase):
    def test_user_registration_form_password_input(self):
        form = UserRegistrationForm()
        form.username = 'TestUser'
        form.email = 'test@mail.com'
        form.password1 = 'Pa55w.rd'
        form.password2 = 'Pa55w,rd'
        self.assertFalse(form.is_valid())


class SnippetFormTest(TestCase):
    def test_snippet_form_name_field_label(self):
        form = SnippetForm()
        self.assertTrue(form.fields['name'].label == 'Имя')

    def test_snippet_form_lang_field_label(self):
        form = SnippetForm()
        self.assertTrue(form.fields['lang'].label == 'Язык')

    def test_snippet_form_code_field_label(self):
        form = SnippetForm()
        self.assertTrue(form.fields['code'].label == 'Код')

    def test_snippet_form_is_private_field_label(self):
        form = SnippetForm()
        self.assertTrue(form.fields['is_private'].label == 'Приватный')


class CommentFormTest(TestCase):
    def test_snippet_form_name_field_label(self):
        form = CommentForm()
        self.assertTrue(form.fields['text'].label == 'Ваш комментарий')

