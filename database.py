import sqlite3


def create_connection():
    return sqlite3.connect("refind.db")


def add_column_if_missing(cursor, table_name, column_name, column_type):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_name TEXT,
        school_code TEXT UNIQUE,
        admin_username TEXT
    )
    """)

    add_column_if_missing(cursor, "schools", "admin_username", "TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        description TEXT,
        category TEXT,
        location_found TEXT,
        date_found TEXT,
        current_location TEXT,
        reported_by TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        description TEXT,
        category TEXT,
        location_lost TEXT,
        date_lost TEXT,
        reported_by TEXT
    )
    """)

    add_column_if_missing(cursor, "found_items", "photo1_path", "TEXT")
    add_column_if_missing(cursor, "found_items", "photo2_path", "TEXT")
    add_column_if_missing(cursor, "found_items", "school_code", "TEXT")

    add_column_if_missing(cursor, "lost_items", "photo1_path", "TEXT")
    add_column_if_missing(cursor, "lost_items", "photo2_path", "TEXT")
    add_column_if_missing(cursor, "lost_items", "school_code", "TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        item_type TEXT,
        claimed_by TEXT,
        reported_by TEXT
    )
    """)

    add_column_if_missing(cursor, "claims", "school_code", "TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_id INTEGER,
        sender TEXT,
        message TEXT,
        sent_at TEXT
    )
    """)

    add_column_if_missing(cursor, "messages", "is_read", "INTEGER DEFAULT 0")

    conn.commit()
    conn.close()


def add_school(school_name, school_code, admin_username):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO schools (school_name, school_code, admin_username)
        VALUES (?, ?, ?)
        """, (school_name, school_code, admin_username))

        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False

    conn.close()
    return success


def get_schools_by_admin(admin_username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM schools
    WHERE admin_username = ?
    ORDER BY school_name
    """, (admin_username,))

    schools = cursor.fetchall()
    conn.close()
    return schools


def is_valid_school_code(school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM schools
    WHERE school_code = ?
    """, (school_code,))

    school = cursor.fetchone()
    conn.close()
    return school is not None


def get_school_name_by_code(school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT school_name FROM schools
    WHERE school_code = ?
    """, (school_code,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return ""


def add_found_item(item_name, description, category, location_found, date_found,
                   current_location, reported_by, photo1_path, photo2_path, school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO found_items
    (item_name, description, category, location_found, date_found,
     current_location, reported_by, photo1_path, photo2_path, school_code)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_name, description, category, location_found, date_found,
        current_location, reported_by, photo1_path, photo2_path, school_code
    ))

    conn.commit()
    conn.close()


def get_found_items(school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM found_items
    WHERE school_code = ?
    """, (school_code,))

    items = cursor.fetchall()
    conn.close()
    return items


def search_found_items(keyword, school_code):
    conn = create_connection()
    cursor = conn.cursor()

    search_text = f"%{keyword}%"

    cursor.execute("""
    SELECT * FROM found_items
    WHERE (item_name LIKE ? OR description LIKE ?)
    AND school_code = ?
    """, (search_text, search_text, school_code))

    items = cursor.fetchall()
    conn.close()
    return items


def add_lost_item(item_name, description, category, location_lost,
                  date_lost, reported_by, photo1_path, photo2_path, school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO lost_items
    (item_name, description, category, location_lost, date_lost,
     reported_by, photo1_path, photo2_path, school_code)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item_name, description, category, location_lost, date_lost,
        reported_by, photo1_path, photo2_path, school_code
    ))

    conn.commit()
    conn.close()


def get_lost_items(school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM lost_items
    WHERE school_code = ?
    """, (school_code,))

    items = cursor.fetchall()
    conn.close()
    return items


def search_lost_items(keyword, school_code):
    conn = create_connection()
    cursor = conn.cursor()

    search_text = f"%{keyword}%"

    cursor.execute("""
    SELECT * FROM lost_items
    WHERE (item_name LIKE ? OR description LIKE ?)
    AND school_code = ?
    """, (search_text, search_text, school_code))

    items = cursor.fetchall()
    conn.close()
    return items


def add_claim(item_id, item_type, claimed_by, reported_by, school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO claims (item_id, item_type, claimed_by, reported_by, school_code)
    VALUES (?, ?, ?, ?, ?)
    """, (item_id, item_type, claimed_by, reported_by, school_code))

    conn.commit()
    conn.close()


def get_user_claims(username, school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM claims
    WHERE (claimed_by = ? OR reported_by = ?)
    AND school_code = ?
    """, (username, username, school_code))

    claims = cursor.fetchall()
    conn.close()
    return claims


def add_message(claim_id, sender, message, sent_at):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO messages (claim_id, sender, message, sent_at, is_read)
    VALUES (?, ?, ?, ?, 0)
    """, (claim_id, sender, message, sent_at))

    conn.commit()
    conn.close()


def get_messages(claim_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM messages
    WHERE claim_id = ?
    ORDER BY id ASC
    """, (claim_id,))

    messages = cursor.fetchall()
    conn.close()
    return messages


def get_unread_message_count(username, school_code):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM messages m
    JOIN claims c ON m.claim_id = c.id
    WHERE (c.claimed_by = ? OR c.reported_by = ?)
    AND c.school_code = ?
    AND m.sender != ?
    AND m.is_read = 0
    """, (username, username, school_code, username))

    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_unread_count_for_claim(claim_id, username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM messages
    WHERE claim_id = ?
    AND sender != ?
    AND is_read = 0
    """, (claim_id, username))

    count = cursor.fetchone()[0]
    conn.close()
    return count


def mark_messages_as_read(claim_id, username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE messages
    SET is_read = 1
    WHERE claim_id = ?
    AND sender != ?
    """, (claim_id, username))

    conn.commit()
    conn.close()


def reset_demo_data():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM claims")
    cursor.execute("DELETE FROM found_items")
    cursor.execute("DELETE FROM lost_items")
    cursor.execute("DELETE FROM schools")

    conn.commit()
    conn.close()

def get_item_title(item_id, item_type):
    conn = create_connection()
    cursor = conn.cursor()

    if item_type == "found":
        cursor.execute("""
        SELECT item_name FROM found_items
        WHERE id = ?
        """, (item_id,))
    else:
        cursor.execute("""
        SELECT item_name FROM lost_items
        WHERE id = ?
        """, (item_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]

    return "Unknown Item"