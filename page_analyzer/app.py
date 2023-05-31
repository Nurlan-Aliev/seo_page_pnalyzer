import os
from flask import (Flask, url_for,
                   render_template, get_flashed_messages,
                   request, redirect, flash, abort)
from page_analyzer import db
from dotenv import load_dotenv
from validators.url import url as validate
from page_analyzer.utils import build_parts
import requests


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = 432000


@app.route('/')
def index():
    return render(200)


@app.route('/error_500')
def er_500():
    abort(500)


@app.get('/urls')
def get_urls():
    conn = db.create_connection()
    table = db.get_urls(conn)
    result = []

    for url in table:

        url_id = url.get('id')
        utl_info = {'url_id': url_id, 'url_name': url.get('name')}
        check_url = db.get_check(conn, url_id)
        dict_parts = build_parts(utl_info, check_url)
        result.append(dict_parts)

    db.close(conn)
    return render_template('urls.html', table=result)


@app.post('/urls')
def post_urls():

    url = request.form.get('url')
    if len(url) < 1:
        flash('URL обязателен', 'alert-danger')

    if not validate(url):

        flash('Некорректный URL', 'alert-danger')
        return render(422)

    if len(url) > 255:

        flash('URL превышает 255 символов', 'alert-danger')
        return render(422)

    conn = db.create_connection()
    url_id = db.get_id(conn, url)

    if not url_id:

        db.create_url(conn, url)
        flash('Страница успешно добавлена', 'alert-success')
        url_id = db.get_id(conn, url)
        db.close(conn)

        return redirect(url_for('urls_id', url_id=url_id)), 302

    else:

        flash('Страница уже существует', 'alert-info')
        db.close(conn)
        return redirect(url_for('urls_id', url_id=url_id)), 302


def render(code):
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages), code


@app.route('/urls/<int:url_id>')
def urls_id(url_id):
    conn = db.create_connection()
    messages = get_flashed_messages(with_categories=True)
    url = db.get_url(conn, url_id)
    checks_url = db.get_check(conn, url_id)
    db.close(conn)
    return render_template('urls_id.html', messages=messages,
                           site=url, checks_url=checks_url)


@app.post('/urls/<int:url_id>/checks')
def check(url_id):
    try:
        conn = db.create_connection()

        url = db.get_url(conn, url_id)
        name = url.get('name')
        response = requests.get(name)
        sk = response.status_code
        db.create_check(conn, url_id, sk, response)
        db.close(conn)
        flash('Страница успешно проверена', 'alert-success')

        if sk > 399:
            flash('Произошла ошибка при проверке', 'alert-danger')
            return redirect(url_for('urls_id', url_id=url_id)), 302

        return redirect(url_for('urls_id', url_id=url_id)), 302

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('urls_id', url_id=url_id)), 302


@app.errorhandler(500)
@app.errorhandler(404)
def page_not_found(error):
    code = error.code
    message = error.description
    title = error.name
    return render_template('error.html', title=title,
                           message=message, code=code), code
