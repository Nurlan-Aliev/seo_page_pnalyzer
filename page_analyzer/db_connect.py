import psycopg2
from psycopg2 import pool
from page_analyzer.setting import DB_HOST, DB_NAME, DB_USER, DB_PORT, DB_PASS
from contextlib import contextmanager


def create_connection(*args, **kwargs):
    """Create connection for work with PostgresSQL"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME)


def create_pool(min_conn=1, max_conn=5):
    return pool.SimpleConnectionPool(
        minconn=min_conn,
        maxconn=max_conn,
        connection_factory=create_connection,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME)


@contextmanager
def get_connection():
    """Get connection from pool or error if connection doesn't work"""

    conn=None
    try:
        conn = conn_pool.getconn()
        yield conn
        conn.commit()
    except Exception as error:
        conn.rollback()
        raise Exception(f'Connection lost. Changes abort. {error}')
    finally:
        if conn:
            conn_pool.putconn(conn)


conn_pool = create_pool()
