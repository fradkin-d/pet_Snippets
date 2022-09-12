from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from MainApp.models import Snippet, SupportedLang, SnippetLike, Comment
import json


class IndexPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user('TestUser')
        test_lang = SupportedLang.objects.create(lang='TestLang')

        number_of_public_snippets = 15
        for snippet_num in range(number_of_public_snippets):
            Snippet.objects.create(
                name=f'Test Snippet {snippet_num}',
                lang=test_lang,
                code='print("Test code")',
                is_private=False,
                author=test_user
            )

        for snippet in Snippet.objects.filter(is_private=False):
            SnippetLike.objects.create(snippet=snippet, author=test_user)
            Comment.objects.create(snippet=snippet, author=test_user, text='Test text')

        number_of_private_snippets = 5
        for snippet_num in range(number_of_private_snippets):
            Snippet.objects.create(
                name=f'Test Private Snippet {snippet_num}',
                lang=test_lang,
                code='print("Test code")',
                is_private=True,
                author=test_user
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/index.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('snippets_count' in response.context)
        self.assertTrue('top_ten_by_rating' in response.context)
        self.assertTrue('top_ten_by_reviews' in response.context)

    def test_list_top_ten_by_rating(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['top_ten_by_rating']) == 10)

    def test_list_top_ten_by_reviews(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['top_ten_by_reviews']) == 10)


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


class SnippetCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='TestUser', password='Pa55w.rd')
        SupportedLang.objects.create(lang='TestLang')

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get('/snippets/add')
        self.assertRedirects(response, '/accounts/login/?next=/snippets/add')

    def test_view_logged_in_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get('/snippets/add')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/add_snippet.html')

    def test_view_validation(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('add_snippet_page'),
            data={
                'name': 'TestName',
                'lang': SupportedLang.objects.get(lang='TestLang'),
                'code': 'TestCode',
                'is_private': False
            },
            follow=True
        )
        self.assertRedirects(response, '/snippets/my_list')
        author = Snippet.objects.get(id=1).author
        user = User.objects.get(username='TestUser')
        self.assertEqual(author, user)

    def test_view_success_redirect(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get(reverse('add_snippet_page'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('add_snippet_page'),
            data={
                'name': 'TestName',
                'lang': SupportedLang.objects.get(lang='TestLang'),
                'code': 'TestCode',
                'is_private': False
            },
            follow=True
        )
        self.assertRedirects(response, '/snippets/my_list')

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue('Сниппет добавлен' in message.message)


class SnippetUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        Snippet.objects.create(
            name='TestName',
            lang=lang,
            code='TestCode',
            is_private=False,
            author=user
        )

    def test_view_redirect_if_not_logged_in(self):
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(f'/snippets/{snippet.slug}/update', follow=True)
        self.assertRedirects(response, f'/accounts/login/?next=/snippets/{snippet.slug}/update')

    def test_view_logged_in_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(f'/snippets/{snippet.slug}/update')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_update_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_update_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_update.html')

    def test_view_success_redirect(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_update_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('snippet_update_page', kwargs={'slug': snippet.slug}),
            data={
                'name': 'TestNameUpdated',
                'lang': SupportedLang.objects.get(lang='TestLang'),
                'code': 'TestCodeUpdated',
                'is_private': False
            },
            follow=True
        )
        self.assertRedirects(response, '/snippets/my_list')

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue("Сниппет обновлен" in message.message)


class SnippetDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        Snippet.objects.create(
            name='TestName',
            lang=lang,
            code='TestCode',
            is_private=False,
            author=user
        )

    def test_view_redirect_if_not_logged_in(self):
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(f'/snippets/{snippet.slug}/delete', follow=True)
        self.assertRedirects(response, f'/accounts/login/?next=/snippets/{snippet.slug}/delete')

    def test_view_logged_in_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(f'/snippets/{snippet.slug}/delete')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_delete_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_delete_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_delete.html')

    def test_view_success_redirect(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_delete_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse('snippet_delete_page', kwargs={'slug': snippet.slug}),
            follow=True
        )
        self.assertRedirects(response, '/snippets/my_list')

        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "alert-success")
        self.assertTrue("Сниппет удален" in message.message)


class SnippetDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        Snippet.objects.create(
            name='TestName',
            lang=lang,
            code='TestCode',
            is_private=False,
            author=user
        )

    def test_view_url_exists_at_desired_location(self):
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(f'/snippets/{snippet.slug}')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_detail.html')

    def test_view_anon_user_have_full_context(self):
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('user' in response.context)
        self.assertTrue('comment_form' in response.context)
        self.assertTrue('anon_user' in response.context)
        self.assertFalse('is_liked' in response.context)

    def test_view_logged_in_have_full_context(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('snippet_detail_page', kwargs={'slug': snippet.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)
        self.assertTrue('user' in response.context)
        self.assertTrue('comment_form' in response.context)
        self.assertTrue('anon_user' in response.context)
        self.assertTrue('is_liked' in response.context)


class SnippetsListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/snippets/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('snippets_list_page'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/snippet_list.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)


class UserSnippetsListViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/snippets/my_list')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('my_snippets_list_page'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('my_snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/my_snippet_list.html')

    def test_view_have_full_context(self):
        response = self.client.get(reverse('my_snippets_list_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('pagename' in response.context)


class SnippetJsonNonPrivateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        Snippet.objects.create(
            name='TestName 1',
            lang=lang,
            code='TestCode 1',
            is_private=False,
            author=user
        )
        Snippet.objects.create(
            name='TestName 2',
            lang=lang,
            code='TestCode 2',
            is_private=False,
            author=user
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/ajax/snippet_non_private/json')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('snippet_non_private_json'))
        self.assertEqual(response.status_code, 200)

    def test_json_response(self):
        snippets = Snippet.objects.all()
        json_response = self.client.get(reverse('snippet_non_private_json'))

        json_response_params = json.loads(json_response.content).keys()
        self.assertTrue('data' in json_response_params)
        self.assertTrue('recordsTotal' in json_response_params)
        self.assertTrue('recordsFiltered' in json_response_params)

        snippets_from_json_response = json.loads(json_response.content)['data']
        self.assertEqual(len(snippets), len(snippets_from_json_response))
        self.assertEqual(snippets[0].to_dict_json(), snippets_from_json_response[0])


class SnippetJsonUserIsAuthorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        user2 = User.objects.create_user(username='TestUser2', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        Snippet.objects.create(
            name='TestName 1',
            lang=lang,
            code='TestCode 1',
            is_private=False,
            author=user
        )
        Snippet.objects.create(
            name='TestName 2',
            lang=lang,
            code='TestCode 2',
            is_private=False,
            author=user2
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        response = self.client.get('/ajax/snippet_user_is_author/json')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')

        response = self.client.get(reverse('snippet_user_is_author_json'))
        self.assertEqual(response.status_code, 200)

    def test_json_response(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        user = User.objects.get(pk=1)
        snippets = Snippet.objects.filter(author=user)
        json_response = self.client.get(reverse('snippet_user_is_author_json'))

        json_response_params = json.loads(json_response.content).keys()
        self.assertTrue('data' in json_response_params)
        self.assertTrue('recordsTotal' in json_response_params)
        self.assertTrue('recordsFiltered' in json_response_params)

        snippets_from_json_response = json.loads(json_response.content)['data']
        self.assertEqual(len(snippets), len(snippets_from_json_response))
        self.assertEqual(snippets[0].to_dict_json(), snippets_from_json_response[0])


class CreateCommentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        Snippet.objects.create(
            name='TestName',
            lang=lang,
            code='TestCode',
            is_private=False,
            author=user
        )

    def test_view_redirect_if_not_logged_in(self):
        response = self.client.get('/comment/create', follow=True)
        self.assertRedirects(response, '/accounts/login/')

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.post('/comment/create', {'snippet': snippet.id, 'text': 'TestText'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.post(reverse('create_comment'), {'snippet': snippet.id, 'text': 'TestText'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_create_comment(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        self.client.post(reverse('create_comment'), {'snippet': snippet.id, 'text': 'TestText'})
        self.assertTrue(Comment.objects.filter(snippet=snippet).exists())


class DeleteCommentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        snippet = Snippet.objects.create(
            name='TestName',
            lang=lang,
            code='TestCode',
            is_private=False,
            author=user
        )
        Comment.objects.create(
            snippet=snippet,
            author=user,
            text='TestText'
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        comment = Comment.objects.get(id=1)
        response = self.client.get(f'/comment/delete/{comment.id}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        comment = Comment.objects.get(id=1)
        response = self.client.get(reverse('delete_comment', kwargs={'pk': comment.id}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_delete_comment(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        comment = Snippet.objects.get(id=1)
        self.client.get(reverse('delete_comment', kwargs={'pk': comment.id}))
        self.assertFalse(Comment.objects.filter(snippet=snippet).exists())


class SwitchSnippetlikeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='TestUser', password='Pa55w.rd')
        lang = SupportedLang.objects.create(lang='TestLang')
        snippet = Snippet.objects.create(
            name='TestName',
            lang=lang,
            code='TestCode',
            is_private=False,
            author=user
        )

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(f'/ajax/switch_snippetlike/{snippet.id}')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        response = self.client.get(reverse('switch_snippetlike', kwargs={'snippet_id': snippet.id}))
        self.assertEqual(response.status_code, 200)

    def test_view_create_and_delete_snippetlike(self):
        self.client.login(username='TestUser', password='Pa55w.rd')
        snippet = Snippet.objects.get(id=1)
        user = User.objects.get(id=1)
        self.client.get(reverse('switch_snippetlike', kwargs={'snippet_id': snippet.id}))
        self.assertTrue(SnippetLike.objects.filter(snippet=snippet, author=user).exists())

        self.client.get(reverse('switch_snippetlike', kwargs={'snippet_id': snippet.id}))
        self.assertFalse(SnippetLike.objects.filter(snippet=snippet, author=user).exists())

