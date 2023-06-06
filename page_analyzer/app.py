import os
from flask import (Flask, url_for,
                   render_template, get_flashed_messages,
                   request, redirect, flash, abort)
from page_analyzer import db
from dotenv import load_dotenv
from validators.url import url as validate
import requests
from page_analyzer.url_parse import parse_url, normalize_url


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render(200)


@app.route('/500')
def er_500():
    abort(500)


@app.get('/urls')
def get_urls():
    conn = db.create_connection()
    urls = db.get_urls(conn)
    result = []

    for url in urls:

        url_id = url.id
        url_info = {'url_id': url_id, 'url_name': url.name}

        check_url = db.get_checks(conn, url_id)
        if check_url:
            url_info['sc'] = check_url[0].status_code
            url_info['created_at'] = check_url[0].created_at

        result.append(url_info)

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
    home_page = normalize_url(url)

    url_id = db.get_url_by_name(conn, home_page)
    if not url_id:
        db.create_url(conn, home_page)
        flash('Страница успешно добавлена', 'alert-success')
        url_id = db.get_url_by_name(conn, home_page)
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
    checks_url = db.get_checks(conn, url_id)
    db.close(conn)
    return render_template('urls_id.html', messages=messages,
                           site=url, checks_url=checks_url)


@app.post('/urls/<int:url_id>/checks')
def check(url_id):
    try:
        conn = db.create_connection()

        url = db.get_url(conn, url_id)
        name = url.name
        response = requests.get(name)
        sc = response.status_code

        if sc > 399:
            flash('Произошла ошибка при проверке', 'alert-danger')
            return redirect(url_for('urls_id', url_id=url_id)), 302

        check_url = parse_url(response)
        db.create_check(conn, url_id, sc, check_url)
        db.close(conn)
        flash('Страница успешно проверена', 'alert-success')

        return redirect(url_for('urls_id', url_id=url_id)), 302

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('urls_id', url_id=url_id)), 302


@app.errorhandler(500)
@app.errorhandler(404)
def error_handler(error):
    code = error.code
    message = error.description
    title = error.name
    return render_template('error.html', title=title,
                           message=message, code=code), code
