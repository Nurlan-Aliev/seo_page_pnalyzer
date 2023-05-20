import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from page_analyzer.url import normalize_url
from dotenv import load_dotenv
from page_analyzer.url_parse import parse_url


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connect(func):
    """
    Decorator to establish a database connection
    @get_connect
    def get_urls(conn, site):
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls")
    """
    def wrapper(*args):
        with psycopg2.connect(DATABASE_URL) as conn:
            result = func(conn, *args)
        return result

    return wrapper


@get_connect
def create_site(conn, site: str):
    home_page = normalize_url(site)
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                    (home_page, created_at))
        conn.commit()


@get_connect
def get_id(conn, site: str) -> str:
    home_page = normalize_url(site)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s;", (home_page,))
        site_id = cur.fetchone()
    if site_id:
        return site_id[0]
    return site_id


@get_connect
def get_site(conn, site_id: str) -> tuple:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s;", (site_id,))
        site = cur.fetchone()
    return site


@get_connect
def get_urls(conn) -> list:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM urls")
        urls_table = cur.fetchall()
    return urls_table


@get_connect
def get_check(conn, url_id: str) -> list:
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute('''
                   SELECT id, url_id, status_code, h1,
                   title, description, DATE(created_at) as created_at
                   FROM url_checks
                   WHERE url_checks.url_id = %s
                   ORDER BY id DESC''', (url_id,))
        check = curs.fetchall()
    return check


@get_connect
def create_check(conn, url_id: str, status_code: str, response: str):

    h1, title, description = parse_url(response)
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute('''INSERT INTO url_checks
        (url_id, status_code, h1, title, description, created_at)
        VALUES (%s, %s, %s, %s, %s, %s);''',
                    (url_id, status_code, h1,
                     title, description, created_at))
        conn.commit()
