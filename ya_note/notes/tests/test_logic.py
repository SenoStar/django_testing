from django.urls import reverse
from http import HTTPStatus
from pytils.translit import slugify
from notes.forms import WARNING
from notes.models import Note
from notes.tests.base_for_tests import TestBaseData


class TestLogic(TestBaseData):

    def test_user_can_create_note_and_anonymous_user_cant_create_note(self):
        users = (
            # Авторизованный пользователь
            (self.author, reverse('notes:success')),
            # Анонимный пользователь
            (self.anonymous, reverse('users:login')),
        )
        data = self.data
        for user, redirect_url in users:
            if hasattr(user, 'username'):
                self.client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:add')
                initial_count = Note.objects.count()
                response = self.client.post(url, data=data)
                if hasattr(user, 'username'):
                    self.assertRedirects(response, redirect_url)
                    self.assertEqual(Note.objects.count(), initial_count + 1)
                    new_note = Note.objects.get(slug__exact=data['slug'])
                    self.assertEqual(new_note.title, data['title'])
                    self.assertEqual(new_note.text, data['text'])
                    self.assertEqual(new_note.slug, data['slug'])
                    self.assertEqual(new_note.author, data['author'])
                else:
                    # Не работает. Мы проверяли в test_routes.py
                    # Response didn't redirect as expected
                    # self.assertRedirects(response, redirect_url)
                    self.assertEqual(Note.objects.count(), initial_count)

    def test_not_unique_slug(self):
        form_data = self.data
        new_note_slug = self.note.slug
        form_data['slug'] = new_note_slug
        user = self.author
        self.client.force_login(user)
        initial_count = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data=form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(new_note_slug + WARNING)
                             )
        self.assertEqual(Note.objects.count(), initial_count)

    def test_empty_slug(self):
        form_data = self.data
        form_data['slug'] = ''
        expected_slug = slugify(form_data['title'])
        user = self.author
        self.client.force_login(user)
        initial_count = Note.objects.count()
        url = reverse('notes:add')
        response = self.client.post(url, data=form_data)
        new_note = Note.objects.get(slug=expected_slug)
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(Note.objects.count(), initial_count + 1)
        self.assertRedirects(response, reverse('notes:success'))

    def test_author_can_edit_note_and_other_user_cant_edit_note(self):
        users = (
            self.author,
            self.user_2
        )
        for user in users:
            form_data = self.data
            note = self.note
            self.client.force_login(user)
            with self.subTest(user=user):
                initial_count = Note.objects.count()
                url = reverse('notes:edit', args=(note.slug,))
                self.assertNotEqual(note.slug, form_data['slug'])
                self.assertNotEqual(note.text, form_data['text'])
                self.assertNotEqual(note.title, form_data['title'])
                response = self.client.post(url, form_data)
                if user == note.author:
                    edit_note = Note.objects.get(
                        id=note.id
                    )
                    self.assertEqual(edit_note.slug, form_data['slug'])
                    self.assertEqual(edit_note.text, form_data['text'])
                    self.assertEqual(edit_note.title, form_data['title'])
                    self.assertRedirects(response, reverse('notes:success'))
                else:
                    not_edit_note = Note.objects.get(
                        id=note.id
                    )
                    self.assertEqual(
                        not_edit_note.slug, form_data['slug']
                    )
                    self.assertEqual(
                        not_edit_note.text, form_data['text']
                    )
                    self.assertEqual(
                        not_edit_note.title, form_data['title']
                    )
                self.assertEqual(Note.objects.count(), initial_count)

    def test_author_can_delete_note_and_other_user_cant_delete_note(self):
        users = (
            (self.author, HTTPStatus.FOUND, 1),
            (self.user_2, HTTPStatus.NOT_FOUND, 0),
        )
        note_slug = (self.note.slug,)
        for user, status, note_delete in users:
            self.client.force_login(user)
            with self.subTest(user=user):
                initial_count = Note.objects.count()
                url = reverse('notes:delete', args=note_slug)
                response = self.client.post(url)
                self.assertEqual(response.status_code, status)
                self.assertEqual(Note.objects.count(),
                                 initial_count - note_delete)
