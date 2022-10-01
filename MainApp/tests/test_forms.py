from django.test import TestCase
from MainApp.forms import SnippetForm


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
