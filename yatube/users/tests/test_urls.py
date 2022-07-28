from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class UserURLTests(TestCase):
    auth_urls_templates = {
        '/auth/password_change/': 'users/password_change.html',
        '/auth/password_change/done/': 'users/password_change_done.html',
    }
    guest_urls_templates = {
        '/auth/login/': 'users/login.html',
        '/auth/logout/': 'users/logged_out.html',
        '/auth/password_reset/': 'users/password_reset.html',
        '/auth/password_reset/done/': 'users/password_reset_done.html',
        '/auth/reset/Mw/set-password/': 'users/reset.html',
        '/auth/reset/done/': 'users/reset_done.html',
        '/auth/signup/': 'users/signup.html',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_url_exists_at_desired_location_authorized(self):
        '''Страница доступна авторизованному пользователю.'''
        for url in self.auth_urls_templates:
            with self.subTest(url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        for url in self.guest_urls_templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_url_redirect_anonymous(self):
        """Страница перенаправляет анонимного пользователя на страницу
        авторизации.
        """
        for url in self.auth_urls_templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_users_url_uses_correct_template_guest(self):
        """Страница общего доступа использует правильный шаблон."""
        for url, template in self.guest_urls_templates.items():
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_users_url_uses_correct_template_auth(self):
        """Страница, доступная авторизованному пользователю, использует
        правильный шаблон.
        """
        for url, template in self.auth_urls_templates.items():
            with self.subTest(url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
