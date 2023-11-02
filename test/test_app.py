import psycopg2
import pytest
from page_analyzer.app import app
from page_analyzer import models
import pook


@pytest.fixture
def postgresql_url(postgresql):
    return postgresql.dsn()


# @pytest.fixture
# def postgresql_url(postgresql):
#     return psycopg2.connect(postgresql.dsn())


models.create_connection = postgresql_url


@pytest.fixture()
def test_app_create():
    test_app = app
    test_app.config.update({
        "TESTING": True,
    })
    yield test_app


@pytest.fixture()
def client(test_app_create):
    return test_app_create.test_client()


def test_home_page_success(client):

    response = client.get('/')
    html = response.data.decode()
    assert response.status_code == 200
    assert '<h1 class="display-3">Анализатор страниц</h1>' in html
    assert '<p class="lead">Бесплатно проверяйте сайты на SEO пригодность</p>' in html


def test_url_page(client):

    response = client.get('/urls')
    html = response.data.decode()
    assert response.status_code == 200
    assert '<h1>Сайты</h1>' in html


def test_page_error_404(client):

    response = client.get('/qwerty')
    assert response.status_code == 404
    assert b'Error 404: The requested URL was not found'\
           in response.data


def test_page_error_500(client):
    response = client.get('/500')
    assert response.status_code == 500
    assert b'Error 500: The server encountered an internal error'\
           in response.data


def test_flash_empty_request(client):

    response = client.post('/urls', data={'url': ''})
    html = response.data.decode()
    assert response.status_code == 422
    assert '<div class="alert alert-danger" role="alert">URL обязателен</div>' in html
    assert '<div class="alert alert-danger" role="alert">Некорректный URL</div>' in html


def test_flash_request_more_255(client):

    url = f'https://g{"o" * 255}ogle.com'
    response = client.post('/urls', data={'url': url})
    html = response.data.decode()
    assert response.status_code == 422
    assert '<div class="alert alert-danger" role="alert">URL превышает 255 символов</div>' in html


def test_flash_request_success(client):

    url = 'https://vk.com/some_page'
    response = client.post('/urls', data={'url': url}, follow_redirects=True)
    html = response.data.decode()
    assert response.status_code == 200
    assert response.request.path == '/urls/1'
    assert '<h1>Сайт: https://google.com</h1>' in html
    assert '<div class="alert alert-success" role="alert">Страница успешно добавлена</div>' in html
    response = client.post('/urls', data={'url': url}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/urls/1'
    assert '<div class="alert alert-info" role="alert">Страница уже существует</div>' in html

@pook.on
def test_flash_testing_success(client):
    pook.get(
        'https://google.com',
        reply=200,
        response_json=[{'text': '<h1>SAY MY NAME!!!</h1>'},
                       {'text': '<title>Google</title>'}])

    response = client.post('/urls/1/checks')

    assert response.status_code == 302

    response = client.get('/urls/1')
    assert response.status_code == 200
    assert 'Страница успешно проверена' in response.data.decode('utf-8')


@pook.on
def test_flash_testing_wrong(client):
    pook.get(
        'http://wrong.com',
        reply=500,
    )

    url = 'http://wrong.com'

    client.post('/urls', data={'url': url}, follow_redirects=True)
    response = client.post('/urls/2/checks')
    assert response.status_code == 302

    response = client.get('/urls/2')
    assert response.status_code == 200
    assert 'Произошла ошибка при проверке' in response.data.decode('utf-8')
