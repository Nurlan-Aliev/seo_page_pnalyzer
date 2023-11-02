import os
from flask import (Flask, url_for,
                   render_template, get_flashed_messages,
                   request, redirect, flash, abort)
from page_analyzer import models
from page_analyzer.db_connect import get_connection
from dotenv import load_dotenv
import requests
from page_analyzer.url_parse import parse_url, normalize_url
from page_analyzer.validator import is_valide

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def render(code):
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages), code


@app.route('/')
def index():
    return render(200)


@app.route('/urls', methods=["GET", "POST"])
def get_urls():
    with get_connection() as conn:

        if request.method == 'POST':
            url = request.form.get('url')
            if is_valide(url):
                return render(422)

            correct_url = normalize_url(url)
            correct_url_id = models.is_url_exist(conn, correct_url)

            if not correct_url_id:
                models.create_url(conn, correct_url)
                flash('Страница успешно добавлена', 'alert-success')
                correct_url_id = models.is_url_exist(conn, correct_url)
                return redirect(url_for('urls_id', url_id=correct_url_id)), 302
            else:
                flash('Страница уже существует', 'alert-info')
                return redirect(url_for('urls_id', url_id=correct_url_id)), 302
        else:
            url_data = models.get_all_urls(conn)
            return render_template('urls.html', table=url_data)


@app.route('/urls/<int:url_id>')
def urls_id(url_id):
    with get_connection() as conn:
        messages = get_flashed_messages(with_categories=True)
        url = models.get_url(conn, url_id)
        checks_url = models.get_checks(conn, url_id)
    return render_template('urls_id.html', messages=messages,
                           site=url, checks_url=checks_url)


@app.post('/urls/<int:url_id>/checks')
def check(url_id):
    try:
        with get_connection() as conn:

            url = models.get_url(conn, url_id)
            name = url.name
            response = requests.get(name)
            sc = response.status_code

        if sc > 399:
            flash('Произошла ошибка при проверке', 'alert-danger')
            return redirect(url_for('urls_id', url_id=url_id)), 302

        check_url = parse_url(response)
        models.create_check(conn, url_id, sc, check_url)
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


@app.route('/500')
def er_500():
    abort(500)
