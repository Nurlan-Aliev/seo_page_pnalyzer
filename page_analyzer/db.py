import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from dotenv import load_dotenv
from page_analyzer.url_parse import parse_url, normalize_url


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def create_connection():
    return psycopg2.connect(DATABASE_URL)


def close(conn):
    conn.close()


def create_url(conn, url: str):
    home_page = normalize_url(url)
    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                    (home_page, created_at))
        conn.commit()


def get_id(conn, url: str) -> str:
    home_page = normalize_url(url)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s;", (home_page,))
        url_id = cur.fetchone()
    if url_id:
        return url_id[0]
    return url_id


def get_url(conn, url_id: str) -> tuple:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s;", (url_id,))
        url = cur.fetchone()
    return url


def get_urls(conn) -> list:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM urls")
        urls_table = cur.fetchall()

    return urls_table


def get_check(conn, url_id) -> list:
    with conn.cursor(cursor_factory=RealDictCursor) as curs:
        curs.execute('''
                   SELECT id, url_id, status_code, h1,
                   title, description, DATE(created_at) as created_at
                   FROM url_checks
                   WHERE url_checks.url_id = %s
                   ORDER BY id DESC''', (url_id,))
        check = curs.fetchall()
    return check


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
