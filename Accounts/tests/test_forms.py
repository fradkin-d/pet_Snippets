from django.test import TestCase
from Accounts.forms import UserRegistrationForm


class UserRegistrationFormTest(TestCase):
    def test_user_registration_form_password_input(self):
        form = UserRegistrationForm()
        form.username = 'TestUser'
        form.email = 'test@mail.com'
        form.password1 = 'Pa55w.rd'
        form.password2 = 'Pa55w,rd'
        self.assertFalse(form.is_valid())
