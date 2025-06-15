print('[payment_service] DEBUG: database.py loaded')
import sqlite3
import os

# Ensure the instance directory exists
os.makedirs('./instance', exist_ok=True)

def get_db_path():
    return os.path.join('./instance', 'payment_service.db')

def init_db():
    db_path = get_db_path()
    print(f"[payment_service] Initializing database at {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS payment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_payment(customer, amount, status, date):
    db_path = get_db_path()
    print(f"[payment_service] add_payment: DB path = {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO payment (customer, amount, status, date)
        VALUES (?, ?, ?, ?)
    ''', (customer, amount, status, date))
    conn.commit()
    payment_id = c.lastrowid
    print(f"[payment_service] add_payment: Inserted payment_id = {payment_id}")
    conn.close()
    return payment_id

def get_all_payments():
    db_path = get_db_path()
    print(f"[payment_service] get_all_payments: DB path = {db_path}")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id, customer, amount, status, date FROM payment')
    rows = c.fetchall()
    print(f"[payment_service] get_all_payments: Found {len(rows)} rows")
    conn.close()
    return [
        {
            'id': row[0],
            'customer': row[1],
            'amount': row[2],
            'status': row[3],
            'date': row[4]
        }
        for row in rows
    ]

def update_payment_status(payment_id, new_status):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('UPDATE payment SET status = ? WHERE id = ?', (new_status, payment_id))
    conn.commit()
    conn.close()
    return True 