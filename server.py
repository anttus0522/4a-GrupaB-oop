from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB = "books.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def needs_fk_migration(cursor, table_name, expected_tables):
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    fk_list = cursor.fetchall()
    return any(fk[2] not in expected_tables for fk in fk_list)


def recreate_table(cursor, table_name, create_sql, columns):
    old_name = f"{table_name}_old"
    cursor.execute(f"ALTER TABLE {table_name} RENAME TO {old_name}")
    cursor.execute(create_sql)
    cols = ", ".join(columns)
    cursor.execute(
        f"INSERT INTO {table_name} ({cols}) SELECT {cols} FROM {old_name}"
    )
    cursor.execute(f"DROP TABLE {old_name}")


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        average_rating REAL,
        ratings_count INTEGER
    )
    """)

    ratings_sql = """
    CREATE TABLE ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        rating REAL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    )
    """

    if table_exists(cursor, "ratings"):
        if needs_fk_migration(cursor, "ratings", ["users", "books"]):
            recreate_table(cursor, "ratings", ratings_sql, ["id", "user_id", "book_id", "rating"])
    else:
        cursor.execute(ratings_sql)

    user_book_sql = """
    CREATE TABLE user_book (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        status TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    )
    """

    if table_exists(cursor, "user_book"):
        if needs_fk_migration(cursor, "user_book", ["users", "books"]):
            recreate_table(cursor, "user_book", user_book_sql, ["id", "user_id", "book_id", "status"])
    else:
        cursor.execute(user_book_sql)

    conn.commit()
    conn.close()


@app.route('/books', methods=['GET'])
def get_books():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()

    books = []
    for r in rows:
        books.append({
            "id": r[0],
            "title": r[1],
            "author": r[2],
            "average_rating": r[3],
            "ratings_count": r[4]
        })

    conn.close()
    return jsonify(books)


@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO books (title, author, average_rating, ratings_count)
        VALUES (?, ?, 0, 0)
    """, (data["title"], data["author"]))

    conn.commit()
    conn.close()

    return {"message": "Knjiga dodana"}

#  RATE
@app.route('/rate', methods=['POST'])
def rate():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ratings (user_id, book_id, rating)
        VALUES (?, ?, ?)
    """, (data["user_id"], data["book_id"], data["rating"]))

    # recalculacija
    cursor.execute("""
        SELECT AVG(rating), COUNT(*)
        FROM ratings
        WHERE book_id=?
    """, (data["book_id"],))

    avg, count = cursor.fetchone()

    cursor.execute("""
        UPDATE books
        SET average_rating=?, ratings_count=?
        WHERE id=?
    """, (round(avg,2), count, data["book_id"]))

    conn.commit()
    conn.close()

    return {"message": "Ocjena spremljena"}

#  STATUS
@app.route('/user_book', methods=['POST'])
def add_status():
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM user_book
        WHERE user_id=? AND book_id=?
    """, (data["user_id"], data["book_id"]))

    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE user_book
            SET status=?
            WHERE user_id=? AND book_id=?
        """, (data["status"], data["user_id"], data["book_id"]))
    else:
        cursor.execute("""
            INSERT INTO user_book (user_id, book_id, status)
            VALUES (?, ?, ?)
        """, (data["user_id"], data["book_id"], data["status"]))

    conn.commit()
    conn.close()

    return {"message": "OK"}


@app.route('/user_book/<int:user_id>')
def my_books(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT books.title, user_book.status
        FROM user_book
        JOIN books ON books.id = user_book.book_id
        WHERE user_book.user_id=?
    """, (user_id,))

    data = [
        {"title": r[0], "status": r[1]}
        for r in cursor.fetchall()
    ]

    conn.close()
    return jsonify(data)

# LOGIN 
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return {"error": "Nevažeće ime"}, 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        user_id = row["id"]
    else:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        user_id = cursor.lastrowid

    conn.close()
    return {"user_id": user_id}

if __name__ == "__main__":
    init_db()
    app.run(debug=True)