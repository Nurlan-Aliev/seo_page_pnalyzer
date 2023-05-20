import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
from page_analyzer.url_parse import parse_url


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connect(func):
    def wrapper(*args):
        with psycopg2.connect(DATABASE_URL) as conn:
            result = func(conn, *args)
        return result

    return wrapper


# @get_connect
# def create_table_urls(conn):
#     if conn.closed == 0:
#         print("connection was open")
#     with conn.cursor() as cur:
#         cur.execute('DROP TABLE IF EXISTS urls;')
#         cur.execute('''CREATE TABLE urls (
#         id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
#         name VARCHAR(255) UNIQUE,
#         created_at DATE);''')
#         conn.commit()


@get_connect
def create_site(conn, site):
    normalize = urlparse(site)
    home_page = f'{normalize.scheme}://{normalize.netloc}'
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                    (home_page, created_at))
        conn.commit()


@get_connect
def get_id(conn, site):
    normalize = urlparse(site)
    home_page = f'{normalize.scheme}://{normalize.netloc}'
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s;", (home_page,))
        site_id = cur.fetchone()
    if site_id:
        return site_id[0]
    return site_id


@get_connect
def get_site(conn, site_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s;", (site_id,))
        site = cur.fetchone()
    return site


@get_connect
def get_urls(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls")
        urls_table = cur.fetchall()
    return urls_table


# @get_connect
# def create_table_checks(conn):
#     with conn.cursor() as cur:
#         cur.execute('DROP TABLE IF EXISTS url_checks;')
#         cur.execute('''CREATE TABLE url_checks (
#         id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
#         url_id INTEGER,
#         status_code INTEGER,
#         h1 VARCHAR(255),
#         title VARCHAR(255),
#         description TEXT,
#         created_at DATE);''')
#         conn.commit()


@get_connect
def get_check(conn, url_id):
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute('''
                   SELECT id, status_code, h1,
                   title, description, DATE(created_at) as created_at, url_id
                   FROM url_checks
                   WHERE url_checks.url_id = %s
                   ORDER BY id DESC''', (url_id,))
        check = curs.fetchall()
        print(check)
    return check

@get_connect
def create_check(conn, url_id, status_code, response):

    h1, title, description = parse_url(response)
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute('''INSERT INTO url_checks
        (url_id, status_code, h1, title, description, created_at)
        VALUES (%s, %s, %s, %s, %s, %s);''',
                    (url_id, status_code, h1,
                     title, description, created_at))
        conn.commit()
