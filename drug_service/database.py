import sqlite3
import os

# Konfigurasi koneksi database SQLite
DATABASE_FILE = "./instance/drug_service.db"

# Ensure the instance directory exists
os.makedirs('./instance', exist_ok=True)

def get_db_connection():
    """Membangun dan mengembalikan koneksi database SQLite."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row # Mengembalikan hasil sebagai objek mirip dictionary
        print(f"Database connection successful: {DATABASE_FILE}")
        return conn
    except sqlite3.Error as e:
        print(f"Error koneksi database: {e}")
        return None

def initialize_drug_database():
    """
    Menginisialisasi database obat jika tabel belum ada.
    Membuat tabel 'drugs' jika belum ada.
    """
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return

        cursor = conn.cursor()

        # Periksa apakah tabel 'drugs' sudah ada
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='drugs'")
        if cursor.fetchone()[0] == 1:
            print("Tabel 'drugs' sudah ada. Tidak perlu membuat ulang.")
            return

        create_table_query = """
        CREATE TABLE drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Tabel 'drugs' berhasil dibuat.")

        # Optional: Tambahkan data dummy untuk pengujian
        try:
            cursor.execute("INSERT INTO drugs (name, description, price, stock, category) VALUES (?, ?, ?, ?, ?)",
                           ("Amoxilin", "Obat antibiotik", 25000.0, 15, "Obat"))
            cursor.execute("INSERT INTO drugs (name, description, price, stock, category) VALUES (?, ?, ?, ?, ?)",
                           ("Paracetamol", "Obat pereda nyeri dan demam", 10000.0, 20, "Obat"))
            conn.commit()
            print("Data dummy obat berhasil ditambahkan.")
        except sqlite3.IntegrityError:
            print("Data dummy sudah ada atau terjadi kesalahan integritas.")
        except sqlite3.Error as e:
            print(f"Error menambahkan data dummy: {e}")

    except sqlite3.Error as e:
        print(f"Error saat inisialisasi database obat: {e}")
    finally:
        if conn:
            conn.close()

def get_all_drugs(search_query=None, category_filter=None):
    """Mengambil semua data obat dari database, dengan opsi pencarian dan filter kategori."""
    conn = get_db_connection()
    if conn is None:
        return []

    drugs = []
    cursor = conn.cursor()
    try:
        sql_query = "SELECT id, name, description, price, stock, category, created_at, updated_at FROM drugs WHERE 1=1"
        params = []

        if search_query:
            sql_query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        if category_filter and category_filter.lower() != 'all':
            sql_query += " AND category LIKE ?"
            params.append(f'%{category_filter}%')

        cursor.execute(sql_query, params)
        drugs = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as err:
        print(f"Error mengambil data obat: {err}")
    finally:
        cursor.close()
        conn.close()
    return drugs

def get_drug_by_id(drug_id):
    """Mengambil data obat tunggal dari database berdasarkan ID."""
    conn = get_db_connection()
    if conn is None:
        return None

    drug = None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, description, price, stock, category, created_at, updated_at FROM drugs WHERE id = ?", (drug_id,))
        row = cursor.fetchone()
        if row:
            drug = dict(row)
    except sqlite3.Error as err:
        print(f"Error mengambil obat dengan ID {drug_id}: {err}")
    finally:
        cursor.close()
        conn.close()
    return drug

def create_drug(name, description, price, stock, category):
    """Menambah obat baru ke database."""
    conn = get_db_connection()
    if conn is None:
        return None

    cursor = conn.cursor()
    query = ("INSERT INTO drugs "
             "(name, description, price, stock, category) "
             "VALUES (?, ?, ?, ?, ?)")
    values = (name, description, price, stock, category)

    try:
        cursor.execute(query, values)
        conn.commit()
        drug_id = cursor.lastrowid
        print(f"Obat baru berhasil ditambahkan dengan ID: {drug_id}")
        return get_drug_by_id(drug_id)
    except sqlite3.Error as err:
        print(f"Error menambah obat baru: {err}. Query: {query}, Values: {values}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def update_drug(drug_id, name=None, description=None, price=None, stock=None, category=None):
    """Memperbarui data obat di database berdasarkan ID."""
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    updates = []
    values = []
    if name is not None:
        updates.append("name = ?")
        values.append(name)
    if description is not None:
        updates.append("description = ?")
        values.append(description)
    if price is not None:
        updates.append("price = ?")
        values.append(price)
    if stock is not None:
        updates.append("stock = ?")
        values.append(stock)
    if category is not None:
        updates.append("category = ?")
        values.append(category)

    if not updates:
        cursor.close()
        conn.close()
        return False

    query = "UPDATE drugs SET " + ", ".join(updates) + ", updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    values.append(drug_id)

    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"Obat dengan ID {drug_id} berhasil diperbarui.")
        return cursor.rowcount > 0
    except sqlite3.Error as err:
        print(f"Error memperbarui obat (ID: {drug_id}): {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def delete_drug(drug_id):
    """Menghapus obat dari database berdasarkan ID."""
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    query = "DELETE FROM drugs WHERE id = ?"
    values = (drug_id,)

    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"Obat dengan ID {drug_id} berhasil dihapus.")
        return cursor.rowcount > 0
    except sqlite3.Error as err:
        print(f"Error menghapus obat (ID: {drug_id}): {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def decrement_drug_stock_atomically(drug_id, quantity_to_decrement):
    """
    Mendekremen stok obat secara atomik.
    Mengembalikan True jika berhasil, False jika stok tidak mencukupi atau terjadi error.
    """
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")
        cursor.execute("SELECT stock FROM drugs WHERE id = ?", (drug_id,))
        result = cursor.fetchone()

        if not result:
            print(f"Obat dengan ID {drug_id} tidak ditemukan.")
            conn.rollback()
            return False

        current_stock = result["stock"]
        if current_stock < quantity_to_decrement:
            print(f"Stok tidak mencukupi untuk obat ID {drug_id}. Stok saat ini: {current_stock}, Diminta: {quantity_to_decrement}")
            conn.rollback()
            return False

        new_stock = current_stock - quantity_to_decrement
        cursor.execute("UPDATE drugs SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_stock, drug_id))

        conn.commit()
        print(f"Stok obat ID {drug_id} berhasil didekremen menjadi {new_stock}.")
        return True
    except sqlite3.Error as err:
        print(f"Error saat mendekremen stok obat ID {drug_id}: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def increment_drug_stock(drug_id, quantity_to_increment):
    """
    Menginkremen stok obat.
    Mengembalikan True jika berhasil, False jika terjadi error.
    """
    conn = get_db_connection()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE drugs SET stock = stock + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (quantity_to_increment, drug_id))
        conn.commit()
        print(f"Stok obat ID {drug_id} berhasil diinkremen.")
        return True
    except sqlite3.Error as err:
        print(f"Error saat menginkremen stok obat ID {drug_id}: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def init_db():
    conn = sqlite3.connect('drug_service.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS drug (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_drug_database() 