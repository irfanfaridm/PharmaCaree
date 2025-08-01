import sqlite3
from flask import g

DATABASE = '/app/instance/articles.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with open('services/article/schema.sql', 'r') as f:
        _schema = f.read()
    db.executescript(_schema)
    db.commit() 