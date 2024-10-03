import pytest
from django.urls import reverse
from http import HTTPStatus
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news, initial_count_comments
):
    form_data_for_comment = {
        'text': 'Текст комментария'
    }
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data_for_comment)
    count_comments = Comment.objects.filter(news=news).count()
    assert count_comments == initial_count_comments


def test_user_can_create_comment(
        author_client, news, initial_count_comments
):
    form_data_for_comment = {
        'text': 'Текст комментария'
    }
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data_for_comment)
    assert response.status_code == HTTPStatus.FOUND
    count_comments = Comment.objects.filter(news=news).count()
    assert count_comments == initial_count_comments + 1


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
def test_user_cant_use_bad_words(
        author_client, news, bad_word, initial_count_comments
):
    form_data_for_comment = {
        'text': f'{bad_word}'
    }
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data_for_comment)
    form = response.context['form']
    assert 'text' in form.errors
    assert form.errors['text'] != [WARNING]
    count_comments = Comment.objects.filter(news=news).count()
    assert count_comments == initial_count_comments


def test_author_can_delete_comment(
        author_client, comment_id, initial_count_comments
):
    url = reverse('news:delete', args=comment_id)
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == initial_count_comments - 1


def test_author_can_edit_comment(
        author_client, comment_id, comment, initial_count_comments
):
    changed_text = 'Другой текст'
    form_data_for_comment = {
        'text': changed_text
    }
    url = reverse('news:edit', args=comment_id)
    response = author_client.post(url, data=form_data_for_comment)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == initial_count_comments
    edit_comment = Comment.objects.get(id=comment_id[0])
    assert edit_comment.text == changed_text
    assert edit_comment.text != comment.text
    assert edit_comment.news == comment.news
    assert edit_comment.author == comment.author
    assert edit_comment.created == comment.created


def test_user_cant_delete_comment_of_another_user(
        not_author_client, comment_id, initial_count_comments
):
    url = reverse('news:delete', args=comment_id)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == initial_count_comments


def test_user_cant_edit_comment_of_another_user(
        not_author_client, comment_id, initial_count_comments
):
    form_data_for_comment = {
        'text': 'Текст комментария'
    }
    url = reverse('news:edit', args=comment_id)
    changed_text = 'Другой текст'
    form_data_for_comment['text'] = changed_text
    response = not_author_client.post(url, data=form_data_for_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == initial_count_comments
