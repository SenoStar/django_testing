import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.test.client import Client
from news.models import News, Comment

COMMENT_COUNT_FOR_TEST = 5


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Текст новости'
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def more_news():
    all_news = [
        News(title=f'Новость {index}',
             text=f'Текст {index}',
             date=datetime.today() - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def more_comments(news, author):
    all_comments = [
        Comment(
            news=news,
            author=author,
            text=f'Текст комментария: {index}',
            created=datetime.today() - timedelta(days=index))
        for index in range(COMMENT_COUNT_FOR_TEST)
    ]
    Comment.objects.bulk_create(all_comments)
    return COMMENT_COUNT_FOR_TEST


@pytest.fixture
def initial_count_comments(news):
    return Comment.objects.filter(news=news).count()
