import os
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Example: postgresql://user:pass@localhost:5432/todo_db")

# Ensure sslmode is set for Neon
if 'sslmode' not in DATABASE_URL:
    DATABASE_URL += '?sslmode=require' if '?' not in DATABASE_URL else '&sslmode=require'

pool = None

def get_pool():
    global pool
    if pool is None:
        pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=DATABASE_URL)
    return pool

@contextmanager
def get_cursor():
    p = get_pool()
    conn = p.getconn()
    try:
        # Test if connection is still alive
        conn.isolation_level
    except psycopg2.OperationalError:
        # Connection was closed, get a new one
        p.putconn(conn, close=True)
        conn = p.getconn()
    
    try:
        cur = conn.cursor()
        yield cur, conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            cur.close()
        except Exception:
            pass
        p.putconn(conn)

def ensure_schema():
    """Create tables if they do not exist."""
    with get_cursor() as (cur, _):
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )