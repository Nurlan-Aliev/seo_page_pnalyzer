import os
from flask import (Flask, url_for,
                   render_template, get_flashed_messages,
                   request, redirect, flash, session)
from page_analyzer.main import add_site, create_table, find_id, find_site, select_all
from dotenv import load_dotenv
from validators.url import url


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def link():
    if session.get('table') is None:
        session['table'] = create_table()
    messages = get_flashed_messages(with_categories=True)
    return render_template('main_page.html', messages=messages)


@app.get('/urls')
def get_urls():
    table = select_all()
    return render_template('urls.html', table=table)


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
    messages = get_flashed_messages(with_categories=True)
    site = find_site(id)
    return render_template('urls_id.html', messages=messages, site=site)
