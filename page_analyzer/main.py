import psycopg2
import os
from datetime import date
from urllib.parse import urlparse
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


def create_table():
    with conn.cursor() as cur:
        cur.execute('DROP TABLE IF EXISTS urls;')
        cur.execute('''CREATE TABLE urls (
        id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name VARCHAR(255) UNIQUE,
        created_at DATE);''')
        conn.commit()


def add_site(site):
    normalize = urlparse(site)
    home_page = f'{normalize.scheme}://{normalize.netloc}'
    created_at = date.today()
    print(created_at)
    with conn.cursor() as cur:
        cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                    (home_page, created_at))
        conn.commit()
        print(date.today())


def find_id(site):
    normalize = urlparse(site)
    home_page = f'{normalize.scheme}://{normalize.netloc}'
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s;", (home_page,))
        id = cur.fetchone()
    if id:
        return id[0]
    return id


def find_site(id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls WHERE id = %s;", (id,))
        site = cur.fetchone()
    return site


def select_all():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM urls")
        table = cur.fetchall()

    return table
