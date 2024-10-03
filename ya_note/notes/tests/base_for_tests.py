from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class TestBaseData(TestCase):

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
        cls.data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
            'author': cls.author,
        }
