import os

import pymysql


def _connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASS", "segreta"),
        database=os.environ.get("DB_NAME", "esempio"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def _ensure_schema(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute("SELECT COUNT(*) AS total FROM items")
        if cursor.fetchone()["total"] == 0:
            cursor.execute(
                "INSERT INTO items (title, note) VALUES (%s, %s)",
                ("Item di esempio", "Inserito automaticamente al primo avvio"),
            )
    conn.commit()


def get_all():
    conn = _connection()
    _ensure_schema(conn)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM items ORDER BY id")
        items = cursor.fetchall()
    conn.close()
    return items


def get(item_id):
    conn = _connection()
    _ensure_schema(conn)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        item = cursor.fetchone()
    conn.close()
    return item


def create(title, note):
    conn = _connection()
    _ensure_schema(conn)
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO items (title, note) VALUES (%s, %s)", (title, note))
        item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": item_id, "title": title, "note": note}


def update(item_id, title, note):
    conn = _connection()
    _ensure_schema(conn)
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE items SET title = %s, note = %s WHERE id = %s",
            (title, note, item_id),
        )
        updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    if not updated:
        return None
    return {"id": item_id, "title": title, "note": note}


def delete_item(item_id):
    conn = _connection()
    _ensure_schema(conn)
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted