from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def link():
    return render_template('main_page.html')


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    pass
