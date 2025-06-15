import sqlite3
from services.article.database import get_db

def init_db():
    try:
        db = get_db()
        with open('services/article/schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()
        db.close()
        print("Article database initialized successfully.")
    except Exception as e:
        print(f"Error initializing article database: {e}")

if __name__ == '__main__':
    init_db() 