from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_pages_use_correct_template_author(self):
        """Namespace:name обращается к правильному шаблону."""
        auth_namespaces_templates = {
            reverse('users:password_change'): 'users/password_change.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:password_reset'): 'users/password_reset.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:reset',
                kwargs={'uidb64': 'Mw', 'token': 'set-password'}
            ): 'users/reset.html',
            reverse('users:reset_done'): 'users/reset_done.html',
            reverse('users:signup'): 'users/signup.html',
        }
        for namespace, template in auth_namespaces_templates.items():
            with self.subTest(value=template):
                response = self.authorized_client.get(namespace)
                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context(self):
        """Страница регистрации сформирована с формой создания нового
        пользователя в контексте."""
        response = self.guest_client.get(reverse('users:signup'))
        form = response.context['form']
        self.assertIsInstance(form, UserCreationForm)
