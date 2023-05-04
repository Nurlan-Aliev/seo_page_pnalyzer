import psycopg2
import os
from datetime import date
from urllib.parse import urlparse
from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')


with psycopg2.connect(DATABASE_URL) as conn:

    def create_table_urls():
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
        with conn.cursor() as cur:
            cur.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                        (home_page, created_at))
            conn.commit()

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

    def select_from_urls():
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls")
            urls_table = cur.fetchall()

        return urls_table

    def create_table_checks():
        with conn.cursor() as cur:
            cur.execute('DROP TABLE IF EXISTS url_checks;')
            cur.execute('''CREATE TABLE url_checks (
            id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            url_id INTEGER,
            status_code INTEGER,
            h1 VARCHAR(255),
            title VARCHAR(255),
            description TEXT,
            created_at DATE);''')
            conn.commit()

    def select_from_check(url_id):
        with conn.cursor() as cur:
            cur.execute('''SELECT * FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC;''', (url_id,))
            table_checks = cur.fetchall()

        return table_checks

    def add_check(url_id, status_code, h1, title, description):
        created_at = date.today()
        with conn.cursor() as cur:
            cur.execute('''INSERT INTO url_checks 
            (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);''',
                        (url_id, status_code, h1,
                         title, description, created_at))
            conn.commit()
