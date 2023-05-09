import os
from flask import (Flask, url_for,
                   render_template, get_flashed_messages,
                   request, redirect, flash, session)
from page_analyzer.utils.logic_psql import (create_table_urls,
                                            add_site, find_id, find_site,
                                            select_from_urls,
                                            create_table_checks,
                                            select_from_check, add_check)
from dotenv import load_dotenv
from validators.url import url
import requests



load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = 432000


@app.route('/', methods=['GET', 'POST'])
def link():
    get_session(create_table_urls, 'table')
    return render()


@app.get('/urls')
def get_urls():
    table = select_from_urls()

    context = {
        'select_from_check': select_from_check
    }
    return render_template('urls.html', table=table, **context)


@app.post('/urls')
def post_urls():

    site = request.form.get('url')
    if len(site) < 1:
        flash('URL обязателен', 'error')
    if not url(site):
        flash('Некорректный URL', 'error')
        return render()

    if len(site) > 255:
        flash('URL превышает 255 символов', 'error')
        return render()

    site_id = find_id(site)
    if not site_id:
        add_site(site)
        flash('Страница успешно добавлена', 'success')
        site_id = find_id(site)
        return redirect(url_for('urls_id', id=site_id)), 302
    else:
        flash('Страница уже существует', 'info')
        return redirect(url_for('urls_id', id=site_id)), 302


def render():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main_page.html', messages=messages), 422


@app.route('/urls/<id>')
def urls_id(id):
    get_session(create_table_checks, 'check')
    messages = get_flashed_messages(with_categories=True)
    site = find_site(id)
    checks_url = select_from_check(id)
    return render_template('urls_id.html', messages=messages,
                           site=site, checks_url=checks_url)


@app.post('/urls/<url_id>/checks')
def check(url_id):
    try:
        site = find_site(url_id)
        response = requests.get(site[1])
        sk = str(response.status_code)

        add_check(url_id, sk, response)
        flash('Страница успешно проверена', 'success')

        return redirect(url_for('urls_id', id=url_id)), 302

    except requests.exceptions.ConnectionError:
        flash('ошибка', 'error')
        return redirect(url_for('urls_id', id=url_id)), 302


def get_session(fun, arg):
    if session.get(arg) is None:
        fun()
        session[arg] = True
