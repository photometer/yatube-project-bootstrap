import shutil
import tempfile

from http import HTTPStatus
from django.contrib.auth import get_user_model
from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Comment
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_usr')
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
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
            image=cls.uploaded,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.posts_count = Post.objects.count()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        uploaded = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Другой текст поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/' + uploaded.name,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        uploaded = SimpleUploadedFile(
            name='small3.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Другой текст поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), self.posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image='posts/' + uploaded.name,
            ).exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_usr')
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            id=99999,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый текст комментария',
        )
        cls.form = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.form_data = {
            'text': 'Другой текст комментария',
        }
        self.comments_count = Comment.objects.count()

    def test_add_comment(self):
        """Валидная форма создает комментарий в Comment."""
        REDIRECT_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id}
        )
        URL = REDIRECT_URL + 'comment/'
        response = self.author.post(URL, data=self.form_data, follow=True)
        self.assertRedirects(response, REDIRECT_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), self.comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(text=self.form_data['text']).exists()
        )
