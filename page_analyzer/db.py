import psycopg2
from psycopg2.extras import NamedTupleCursor
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


def create_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def close(conn):
    conn.close()


def create_url(conn, url: str):

    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                    (url, created_at))
        conn.commit()


def get_url_by_name(conn, home_page: str):

    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s;", (home_page,))
        url_id = cur.fetchone()
    if url_id:
        return url_id.id
    return url_id


def get_url(conn, url_id: str) -> tuple:
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s;", (url_id,))
        url = cur.fetchone()
    return url


def get_urls(conn) -> list:
    with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
        cur.execute("SELECT * FROM urls")
        urls = cur.fetchall()

    return urls


def get_checks(conn, url_id) -> tuple:
    with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
        curs.execute('''
                   SELECT id, url_id, status_code, h1,
                   title, description, DATE(created_at) as created_at
                   FROM url_checks
                   WHERE url_checks.url_id = %s
                   ORDER BY id DESC''', (url_id,))
        check = curs.fetchall()
    return check


def create_check(conn, url_id: str, status_code: str, check: tuple):

    created_at = datetime.now()
    with conn.cursor() as cur:
        cur.execute('''INSERT INTO url_checks
        (url_id, status_code, h1, title, description, created_at)
        VALUES (%s, %s, %s, %s, %s, %s);''',
                    (url_id, status_code, *check, created_at))
        conn.commit()
