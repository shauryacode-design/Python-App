import os
import traceback
from app import db, app

def get_effective_db_url():
    # app.py already normalizes postgres:// -> postgresql:// but show what we are using here
    url = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI') or 'sqlite:///real_estate.db'
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url

with app.app_context():
    print('Using DATABASE_URL =', get_effective_db_url())
    try:
        db.create_all()
        print("✓ All tables created (or already exist) in the configured database")
    except Exception as e:
        print('❌ Failed to create tables. See traceback below:')
        traceback.print_exc()
        print('\nCommon causes:')
        print(' - DATABASE_URL is missing or incorrect. Ensure you set the env var DATABASE_URL.')
        print(' - Password or special chars need URL-encoding. Encode with urllib.parse.quote_plus')
        print(' - The DB host may not be reachable from this machine (internal hostnames like *.internal are often private).')
        print(' - SSL may be required (append ?sslmode=require to the DATABASE_URL).')
        raise

