import pytest
from pytest_django.asserts import assertRedirects
from http import HTTPStatus
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news')),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    if args is not None:
        args = (args.id,)
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        'news:delete',
        'news:edit',
    ),
)
def test_pages_availability_for_different_users(
    parametrized_client, expected_status, name, comment_id
):
    url = reverse(name, args=comment_id)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        'news:delete', 'news:edit',
    ),
)
def test_redirects(client, name, comment_id):
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
