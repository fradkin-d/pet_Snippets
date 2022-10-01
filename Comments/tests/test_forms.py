from django.test import TestCase
from Comments.forms import CommentForm


class CommentFormTest(TestCase):
    def test_snippet_form_name_field_label(self):
        form = CommentForm()
        self.assertTrue(form.fields['text'].label == 'Ваш комментарий')
