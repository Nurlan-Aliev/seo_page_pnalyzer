import os
from flask import (Flask, url_for,
                   render_template, get_flashed_messages,
                   request, redirect, flash, session)
from page_analyzer.logic_psql import (create_table_urls,
                                      add_site, find_id, find_site,
                                      select_from_urls, create_table_checks,
                                      select_from_check, add_check)
from dotenv import load_dotenv
from validators.url import url
import requests
from bs4 import BeautifulSoup


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = 432000


@app.route('/')
def link():
    if session.get('table') is None:
        create_table_urls()
        session['table'] = True
    messages = get_flashed_messages(with_categories=True)
    return render_template('main_page.html', messages=messages)


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
        return redirect(url_for('link'))

    elif len(site) <= 255:
        id = find_id(site)
        if not id:
            add_site(site)
            flash('Страница успешно добавлена', 'success')
            id = find_id(site)
            return redirect(f'/urls/{id}')
        else:
            flash('Страница уже существует', 'info')
            return redirect(f'/urls/{id}')

    else:
        flash('URL превышает 255 символов', 'error')
        return redirect(url_for('link'))


@app.route('/urls/<id>')
def urls_id(id):
    if session.get('check') is None:
        create_table_checks()
        session['check'] = True
    messages = get_flashed_messages(with_categories=True)
    site = find_site(id)
    checks_url = select_from_check(id)
    return render_template('urls_id.html', messages=messages,
                           site=site, checks_url=checks_url)


@app.post('/urls/<url_id>/checks')
def check(url_id):
    site = find_site(url_id)
    response = requests.get(site[1])
    sk = response.status_code
    soup = BeautifulSoup(response.content, 'html.parser')
    h1 = ''

    if soup.h1:
        h1 = soup.h1.text

    title = ''
    if soup.title:
        title = soup.title.text

    description = ''
    for i in soup.find_all('meta'):
        if i.get('name') == 'description':
            description = i.get('content')

    add_check(url_id, sk, h1, title, description)
    flash('Страница успешно проверена', 'success')
    return redirect(f'/urls/{url_id}'), 302
