import validators
from flask import flash


def is_valide(url):
    '''Valide url and return None or True if url isn't valide'''
    if len(url) < 1:
        flash('URL обязателен', 'alert-danger')

    if not validators.url(url):
        flash('Некорректный URL', 'alert-danger')
        return True

    if len(url) > 255:
        flash('URL превышает 255 символов', 'alert-danger')
        return True
