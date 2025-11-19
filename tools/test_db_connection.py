from sqlalchemy import create_engine, text
import os
from urllib.parse import quote_plus

def test_connection():
    url = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI')
    if not url:
        print('DATABASE_URL not set')
        return
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    print('Attempting to connect to', url)
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            res = conn.execute(text('SELECT version();'))
            print('Postgres version:', res.fetchone()[0])
            res = conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"))
            print('Tables in public schema (count):', res.fetchone()[0])
    except Exception as e:
        print('Connection failed:', type(e).__name__, e)

if __name__ == '__main__':
    test_connection()
