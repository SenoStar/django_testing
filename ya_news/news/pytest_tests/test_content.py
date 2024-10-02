import pytest
from django.urls import reverse
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(
    client, count_more_news
):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == count_more_news


@pytest.mark.django_db
def test_news_order(client, sorted_dates_more_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted_dates_more_news


@pytest.mark.django_db
def test_comments_order(client, news_id, sorted_created_more_comment):
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert sorted_timestamps == sorted_created_more_comment


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_id):
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.parametrize(
    'parametrized_client',
    (
        pytest.lazy_fixture('author_client'),
    ),
)
def test_authorized_client_has_form(parametrized_client, news_id):
    url = reverse('news:detail', args=news_id)
    response = parametrized_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
