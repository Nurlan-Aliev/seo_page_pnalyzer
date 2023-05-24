import os
from flask import (Flask, url_for,
                   render_template, get_flashed_messages,
                   request, redirect, flash)
from page_analyzer import db
from dotenv import load_dotenv
from validators.url import url
import requests


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = 432000


@app.route('/')
def urls():
    return render(200)


@app.get('/urls')
def get_urls():
    table = db.get_urls()
    context = {
        'get_check': db.get_check
    }
    return render_template('urls.html', table=table, **context)


@app.post('/urls')
def post_urls():

    site = request.form.get('url')
    if len(site) < 1:
        flash('URL обязателен', 'alert-danger')
    if not url(site):
        flash('Некорректный URL', 'alert-danger')
        return render(422)

    if len(site) > 255:
        flash('URL превышает 255 символов', 'alert-danger')
        return render(422)

    site_id = db.get_id(site)
    if not site_id:
        db.create_site(site)
        flash('Страница успешно добавлена', 'alert-success')
        site_id = db.get_id(site)
        return redirect(url_for('urls_id', url_id=site_id)), 302
    else:
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('urls_id', url_id=site_id)), 302


def render(code):
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages), code


@app.route('/urls/<url_id>')
def urls_id(url_id):
    messages = get_flashed_messages(with_categories=True)
    site = db.get_site(url_id, )
    checks_url = db.get_check(url_id, )
    return render_template('urls_id.html', messages=messages,
                           site=site, checks_url=checks_url)


@app.post('/urls/<url_id>/checks')
def check(url_id):
    try:
        site = db.get_site(url_id, )
        response = requests.get(site[1])
        sk = response.status_code
        db.create_check(url_id, sk, response, )
        flash('Страница успешно проверена', 'alert-success')

        if sk > 399:
            flash('Произошла ошибка при проверке', 'alert-danger')
            return redirect(url_for('urls_id', url_id=url_id)), 302

        return redirect(url_for('urls_id', url_id=url_id)), 302

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('urls_id', url_id=url_id)), 302


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404
