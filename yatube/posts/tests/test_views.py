import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_usr')
        cls.user_following = User.objects.create_user(username='test_usr_2')
        cls.author = Client()
        cls.author.force_login(cls.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            id=99999,
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый текст комментария',
        )
        Follow.objects.create(
            user=cls.user_following,
            author=cls.user,
        )
        Follow.objects.create(
            user=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user_auth = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_auth)
        self.follows_count = Follow.objects.count()

    def test_posts_pages_use_correct_template_author(self):
        """Namespace:name обращается к правильному шаблону."""
        author_namespaces_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.post.author}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}): (
                'posts/post_create.html'
            ),
        }
        for namespace, template in author_namespaces_templates.items():
            with self.subTest(template):
                response = self.author.get(namespace)
                self.assertTemplateUsed(response, template)

    def test_edit_or_create_post_page_show_correct_context(self):
        """Страницы создания и редактирования поста сформированы с правильным
        контекстом."""
        form_urls = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for url in form_urls:
            with self.subTest(value=url):
                response = self.author.get(url)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)

    def test_post_detail_pages_list_is_1(self):
        response = self.author.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertIsInstance(response.context['post'], Post)

    def test_post_index_cache(self):
        response = self.author.get('posts:index')
        content = response.content
        Post.objects.get(pk=self.post.id).delete()
        new_response = self.author.get('posts:index')
        self.assertEqual(content, new_response.content)

    def test_posts_list_pages_show_correct_context(self):
        """Шаблоны со списками постов сформированы с правильным контекстом."""
        list_urls_kwargs = {
            reverse('posts:index'): {'filtered': {}, 'kwarg': {}},
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): {
                'filtered': {'group': self.group, },
                'kwarg': {'group.slug': self.group.slug}
            },
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}): {
                    'filtered': {'author_name': self.post.author.username},
                    'kwarg': {}
            },
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}): {
                'filtered': {}, 'kwarg': {},
            }
        }
        for url, filters_kwargs in list_urls_kwargs.items():
            with self.subTest(value=url):
                response = self.author.get(url)
                if 'page_obj' in response.context:
                    first_obj = response.context['page_obj'][0]
                else:
                    first_obj = response.context['post']
                post_text_0 = first_obj.text
                post_group_0 = first_obj.group.title
                post_author_0 = first_obj.author.username
                post_image_0 = first_obj.image
                for filter, filter_value in (
                    filters_kwargs['filtered'].items()
                ):
                    self.assertEqual(response.context[filter], filter_value)
                for kwarg, kwarg_value in filters_kwargs['kwarg'].items():
                    post_kwarg_0 = eval('first_obj.' + kwarg)
                    self.assertEqual(post_kwarg_0, kwarg_value)
                self.assertEqual(post_text_0, self.post.text)
                self.assertEqual(post_group_0, self.group.title)
                self.assertEqual(post_author_0, self.post.author.username)
                self.assertEqual(post_image_0, self.post.image)

    def test_post_with_specified_group_is_shown_on_correct_pages(self):
        """Если при создании поста указать группу, то пост появляется на
        праивльных страницах."""
        group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2'
        )
        post = Post.objects.create(
            author=self.user,
            text='Тестовый текст поста 2',
            id=999,
            group=group,
        )
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={'username': post.author.username}
            ),
            reverse('posts:group_list', kwargs={'slug': group.slug}))
        for url in urls:
            with self.subTest(value=url):
                response = self.author.get(url)
                self.assertIn(post, response.context['page_obj'])
        other_group_response = self.author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertNotIn(post, other_group_response.context['page_obj'])

    def test_post_comment_is_shown_on_post_page(self):
        """После успешной отправки комментарий появляется на странице
        поста."""
        response = self.author.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertIn(self.comment, response.context['comments'])

    def test_auth_user_can_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей."""
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author.username}
            ),
            follow=True,
        )
        self.assertEqual(Follow.objects.count(), self.follows_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_auth,
                author=self.post.author,
            ).exists()
        )

    def test_auth_user_can_unfollow(self):
        """Авторизованный пользователь может отписываться от других
        пользователей."""
        auth_following_client = Client()
        auth_following_client.force_login(self.user_following)
        auth_following_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post.author.username}
            ),
            follow=True,
        )
        self.assertEqual(Follow.objects.count(), self.follows_count - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_auth,
                author=self.post.author,
            ).exists()
        )

    def test_post_new_post_is_shown_on_following_pages(self):
        """Новая запись пользователя появляется в ленте подписанных."""
        Follow.objects.create(
            user=self.user_auth,
            author=self.post.author
        )
        post = Post.objects.create(
            author=self.user,
            text='Тестовый текст поста 3',
            id=99,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'])

    def test_post_new_post_is_not_shown_on_not_following_pages(self):
        """Новая запись пользователя не появляется в списке неподписанных."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый текст поста 3',
            id=99,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POSTS_ON_PAGE = 10
        cls.user = User.objects.create_user(username='test_usr')
        cls.user_auth = User.objects.create_user(username='test_auth')
        cls.author = Client()
        cls.auth = Client()
        cls.author.force_login(cls.user)
        cls.auth.force_login(cls.user_auth)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        bulk_posts = [
            Post(
                author=cls.user,
                text=f'Тестовый текст поста {i}',
                id=i,
                group=cls.group,
            )
            for i in range(cls.POSTS_ON_PAGE + 3)
        ]
        cls.post = Post.objects.bulk_create(bulk_posts)
        Follow.objects.create(
            user=cls.user_auth,
            author=cls.user
        )

    def setUp(self):
        self.urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            reverse('posts:follow_index'),
        )

    def test_posts_first_page_contains_ten_records(self):
        for url in self.urls:
            with self.subTest(value=url):
                response = self.auth.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    self.POSTS_ON_PAGE)

    def test_posts_second_page_contains_three_records(self):
        for url in self.urls:
            with self.subTest(value=url):
                response = self.auth.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
