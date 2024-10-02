from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.user_2 = User.objects.create(username='User2')
        cls.anonymous = Client()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_availability_pages_for_all(self):
        urls = (
            'notes:home',
            'users:signup',
            'users:login',
            'users:logout',
        )
        users = (
            self.author,  # Авторизованный пользователь
            self.anonymous,         # Анонимный пользователь
        )
        for user in users:
            if hasattr(user, 'username'):
                self.client.force_login(user)
            for name in urls:
                # Попытался сделать проверку для анонимов и залогиненых
                # юзеров в одном тесте. Думаю в одном тесте мы ещё
                # проверим notes:home для всех
                with self.subTest(user=user, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_pages_for_user(self):
        user, status = self.author, HTTPStatus.OK
        self.client.force_login(user)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(user=user, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, status)

    def test_availability_pages_note_delete_edit(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.user_2, HTTPStatus.NOT_FOUND),
        )
        note_slug = (self.note.slug,)
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=note_slug)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous(self):
        login_url = reverse('users:login')
        note_slug = (self.note.slug,)
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', note_slug),
            ('notes:edit', note_slug),
            ('notes:delete', note_slug),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
