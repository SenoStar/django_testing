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
def news_id(news):
    return (news.id,)


@pytest.fixture
def form_data_for_comment():
    return {'text': 'Текст комментария'}


@pytest.fixture
def comment(author, news, form_data_for_comment):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=form_data_for_comment['text']
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
    return News.objects.bulk_create(all_news)


# В функции test_news_count увидел неиспользуемый more_news.
# Думал как можно создать новости и посчитать количество постов.
# Сделал вот такую фикстуру, которая даёт нам количество нужных постов,
# а также создаёт новости
@pytest.fixture
def count_more_news(more_news):
    return settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def sorted_dates_more_news(count_more_news):
    return list(
        News.objects.values_list(
            'date',
            flat=True
        ).order_by('-date')[:count_more_news])


@pytest.fixture
def more_comments(news, author, form_data_for_comment):
    all_comments = [
        Comment(
            news=news,
            author=author,
            text=f'{form_data_for_comment['text']} {index}',
            created=datetime.today() - timedelta(days=index))
        for index in range(COMMENT_COUNT_FOR_TEST)
    ]
    return Comment.objects.bulk_create(all_comments)


@pytest.fixture
def sorted_created_more_comment(more_comments):
    return list(
        Comment.objects.values_list(
            'created',
            flat=True
        ).order_by('created')[:COMMENT_COUNT_FOR_TEST])


@pytest.fixture
def initial_count_comments(news):
    return Comment.objects.filter(news=news).count()