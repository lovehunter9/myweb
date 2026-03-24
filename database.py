import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'app.db')


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS calculator_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS generated_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            input_params TEXT NOT NULL,
            output TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_generated_type ON generated_items(type);
        CREATE INDEX IF NOT EXISTS idx_calc_created ON calculator_history(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_gen_created ON generated_items(created_at DESC);
    ''')
    conn.commit()
    conn.close()


def save_calculation(expression: str, result: str) -> int:
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO calculator_history (expression, result) VALUES (?, ?)',
        (expression, result)
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_calculations(limit: int = 50) -> list:
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM calculator_history ORDER BY created_at DESC LIMIT ?',
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_generated_item(item_type: str, input_params: dict, output: dict) -> int:
    conn = get_db()
    cursor = conn.execute(
        'INSERT INTO generated_items (type, input_params, output) VALUES (?, ?, ?)',
        (item_type, json.dumps(input_params, ensure_ascii=False),
         json.dumps(output, ensure_ascii=False))
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_generated_items(item_type: str, limit: int = 50) -> list:
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM generated_items WHERE type = ? ORDER BY created_at DESC LIMIT ?',
        (item_type, limit)
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d['input_params'] = json.loads(d['input_params'])
        d['output'] = json.loads(d['output'])
        results.append(d)
    return results


def delete_generated_item(item_id: int) -> bool:
    conn = get_db()
    cursor = conn.execute('DELETE FROM generated_items WHERE id = ?', (item_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def delete_calculation(calc_id: int) -> bool:
    conn = get_db()
    cursor = conn.execute('DELETE FROM calculator_history WHERE id = ?', (calc_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def clear_calculations() -> int:
    conn = get_db()
    cursor = conn.execute('DELETE FROM calculator_history')
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count
