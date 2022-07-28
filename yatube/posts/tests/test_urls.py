from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.group = Group.objects.create(
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            id=99999,
            group=cls.group,
        )
        cls.author_urls_templates = {
            f'/posts/{cls.post.id}/edit/': 'posts/post_create.html',
        }
        cls.auth_urls_templates = {
            '/create/': 'posts/post_create.html',
            f'/posts/{cls.post.id}/comment/': '',
            f'/profile/{cls.post.author.username}/follow/': '',
            f'/profile/{cls.post.author.username}/unfollow/': '',
        }
        cls.only_auth_urls_templates = {
            f'/profile/{cls.post.author.username}/follow/': '',
            f'/profile/{cls.post.author.username}/unfollow/': '',
        }
        cls.not_guest_urls_templates = {
            **cls.auth_urls_templates,
            **cls.author_urls_templates
        }
        cls.guest_urls_templates = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_url_exists_at_desired_location_author(self):
        """Страница доступна автору."""
        for url in self.author_urls_templates:
            with self.subTest(url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_exists_at_desired_location_authorized(self):
        """Страница доступна авторизованному пользователю."""
        for url, template in self.auth_urls_templates.items():
            with self.subTest(url):
                response = self.authorized_client.get(url)
                if template:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""
        for url in self.guest_urls_templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_url_not_exists(self):
        """Страница не существует."""
        response = self.guest_client.get('/unexisting-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_url_redirect_anonymous(self):
        """Страница перенаправляет анонимного пользователя на страницу
        авторизации.
        """
        for url in self.not_guest_urls_templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_posts_url_redirect_auth(self):
        """Страница перенаправляет авторизованного пользователя."""
        for url in self.author_urls_templates:
            with self.subTest(url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_posts_url_redirect_author(self):
        """Страница перенаправляет автора."""
        for url in self.only_auth_urls_templates:
            with self.subTest(url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_posts_url_uses_correct_template_guest(self):
        """Страница общего доступа использует правильный шаблон."""
        for url, template in self.guest_urls_templates.items():
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_posts_url_uses_correct_template_auth(self):
        """Страница, доступная авторизованному пользователю, использует
        правильный шаблон.
        """
        for url, template in self.auth_urls_templates.items():
            with self.subTest(url):
                response = self.authorized_client.get(url)
                if template:
                    self.assertTemplateUsed(response, template)

    def test_posts_url_uses_correct_template_guest(self):
        """Страница, доступная автору, использует правильный шаблон."""
        for url, template in self.author_urls_templates.items():
            with self.subTest(url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
