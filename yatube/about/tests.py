from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    urls_templates = {
        '/about/author/': 'about/author.html',
        '/about/tech/': 'about/tech.html',
    }

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/."""
        for url in self.urls_templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для адресов /about/."""
        for url, template in self.urls_templates.items():
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)


class StaticPagesViewsTests(TestCase):
    namespaces_templates = {
        reverse('about:author'): 'about/author.html',
        reverse('about:tech'): 'about/tech.html',
    }

    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_use_correct_template_author(self):
        """Namespace:name обращается к правильному шаблону."""
        for namespace, template in self.namespaces_templates.items():
            with self.subTest(template):
                response = self.guest_client.get(namespace)
                self.assertTemplateUsed(response, template)
