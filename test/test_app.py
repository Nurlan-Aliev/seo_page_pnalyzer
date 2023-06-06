import pytest
from page_analyzer.app import app
import pook
import psycopg2
import os
from dotenv import load_dotenv
from page_analyzer import db


load_dotenv()


def create_fake_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL_TEST'))


db.create_connection = create_fake_connection


@pytest.fixture
def client():

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page_success(client):

    response = client.get('/')
    assert response.status_code == 200
    assert 'Анализатор страниц' in response.data.decode('utf-8')


def test_url_page(client):

    response = client.get('/urls')
    assert response.status_code == 200
    assert 'Сайты' in response.data.decode('utf-8')


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
    assert response.status_code == 422
    assert 'URL обязателен' in response.data.decode('utf-8')
    assert 'Некорректный URL' in response.data.decode('utf-8')


def test_flash_request_more_255(client):

    url = f'https://g{"o" * 255}ogle.com'
    response = client.post('/urls', data={'url': url})
    assert response.status_code == 422
    assert 'URL превышает 255 символов' in response.data.decode('utf-8')


def test_flash_request_success(client):

    url = 'https://google.com/some_page'
    response = client.post('/urls', data={'url': url}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/urls/1'
    assert 'Страница успешно добавлена' in response.data.decode('utf-8')
    response = client.post('/urls', data={'url': url}, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/urls/1'
    assert 'Страница уже существует' in response.data.decode('utf-8')


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
