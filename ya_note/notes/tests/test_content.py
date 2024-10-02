from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.user_2 = User.objects.create(username='User2')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        users = (
            (self.author, True),
            (self.user_2, False),
        )
        note = self.note
        for user, bool_notes_list in users:
            self.client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertIs((note in object_list), bool_notes_list)

    def test_pages_contains_form(self):
        user = self.author
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(user)
        for name, args in urls:
            with self.subTest(user=user, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                context = response.context
                self.assertIn('form', context)
                self.assertIsInstance(context['form'], NoteForm)
