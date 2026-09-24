import sqlite3
import os
import hashlib
import json
from datetime import datetime

DB_DIR = os.getenv('DB_DIR', os.path.dirname(__file__))
DB_PATH = os.path.join(DB_DIR, 'platform.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        credits_balance INTEGER DEFAULT 20,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS credit_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        reference_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        service_type TEXT NOT NULL,
        credits_cost INTEGER NOT NULL,
        input_params TEXT,
        output_result TEXT,
        status TEXT DEFAULT 'COMPLETED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    # Ensure default demo user exists for instant zero-friction usage
    cursor.execute('SELECT COUNT(*) FROM users WHERE id = 1')
    if cursor.fetchone()[0] == 0:
        pwd_hash = hash_password('demo123')
        cursor.execute(
            'INSERT INTO users (id, email, password_hash, full_name, credits_balance) VALUES (1, ?, ?, ?, ?)',
            ('demo@example.com', pwd_hash, 'عميل تجريبي', 25)
        )
    conn.commit()
    conn.close()

def create_user(email: str, password: str, full_name: str, initial_credits: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        cursor.execute(
            'INSERT INTO users (email, password_hash, full_name, credits_balance) VALUES (?, ?, ?, ?)',
            (email.lower().strip(), pwd_hash, full_name.strip(), initial_credits)
        )
        user_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO credit_transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)',
            (user_id, initial_credits, 'SIGNUP_BONUS', 'رصيد ترحيبي مجاني لتجربة الخدمات')
        )
        conn.commit()
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    cursor.execute(
        'SELECT * FROM users WHERE email = ? AND password_hash = ?',
        (email.lower().strip(), pwd_hash)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, full_name, credits_balance, created_at FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, full_name, credits_balance, created_at FROM users WHERE email = ?', (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def deduct_credits(user_id: int, amount: int, description: str, reference_id: str = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT credits_balance FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if not row or row['credits_balance'] < amount:
            return False
        cursor.execute('UPDATE users SET credits_balance = credits_balance - ? WHERE id = ?', (amount, user_id))
        cursor.execute(
            'INSERT INTO credit_transactions (user_id, amount, type, description, reference_id) VALUES (?, ?, ?, ?, ?)',
            (user_id, -amount, 'SERVICE_USAGE', description, reference_id)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def add_credits(user_id: int, amount: int, description: str, reference_id: str = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE users SET credits_balance = credits_balance + ? WHERE id = ?', (amount, user_id))
        cursor.execute(
            'INSERT INTO credit_transactions (user_id, amount, type, description, reference_id) VALUES (?, ?, ?, ?, ?)',
            (user_id, amount, 'DEPOSIT', description, reference_id)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def record_task(task_id: str, user_id: int, service_type: str, credits_cost: int, input_params: dict, output_result: dict, status: str = 'COMPLETED'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (id, user_id, service_type, credits_cost, input_params, output_result, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (task_id, user_id, service_type, credits_cost, json.dumps(input_params, ensure_ascii=False), json.dumps(output_result, ensure_ascii=False), status)
    )
    # Ensure default demo user exists for instant zero-friction usage
    cursor.execute('SELECT COUNT(*) FROM users WHERE id = 1')
    if cursor.fetchone()[0] == 0:
        pwd_hash = hash_password('demo123')
        cursor.execute(
            'INSERT INTO users (id, email, password_hash, full_name, credits_balance) VALUES (1, ?, ?, ?, ?)',
            ('demo@example.com', pwd_hash, 'عميل تجريبي', 25)
        )
    conn.commit()
    conn.close()

def get_user_tasks(user_id: int, limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_user_transactions(user_id: int, limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM credit_transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
