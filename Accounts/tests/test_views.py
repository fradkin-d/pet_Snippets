from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegistrationViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/registration/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/registration.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('form' in response.context)

    def test_registration_success_message(self):
        response = self.client.post(
            reverse('registration'),
            data={
                'username': 'TestUser',
                'email': 'test@mail.com',
                'password1': 'Pa55w.rd',
                'password2': 'Pa55w.rd'
            },
            follow=True
        )
        self.assertRedirects(response, reverse('home'))

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue("Регистрация прошла успешно!" in message.message)

    def test_registration_failure_message(self):
        response = self.client.post(
            reverse('registration'),
            data={
                'username': 'TestUser',
                'email': 'test@mail.com',
                'password1': 'Pa55w.rd',
                'password2': 'Pa55w,rd'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-danger")
        self.assertTrue("Ошибка регистрации! Проверьте правильность заполнения формы" in message.message)


class LoginViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/login.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)

    def test_login_success_message(self):
        User.objects.create_user(username='TestUser', password='Pa55w.rd')

        response = self.client.post(
            reverse('login'),
            data={
                'username': 'TestUser',
                'password': 'Pa55w.rd'
            },
            follow=True
        )
        self.assertRedirects(response, reverse('home'))

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue(f'Добро пожаловать, TestUser!' in message.message)

    def test_login_failure_message(self):
        response = self.client.post(
            reverse('login'),
            data={
                'username': 'TestUser',
                'password': 'Pa55w,rd'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-danger")
        self.assertTrue('Ошибка входа! Проверьте правильность заполнения формы' in message.message)


class LogoutViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/accounts/logout/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_logout_message(self):
        response = self.client.post(
            reverse('login'),
            data={
                'username': 'TestUser',
                'password': 'Pa55w,rd'
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue('Выполнен выход' in message.message)
