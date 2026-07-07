import sqlite3
import bcrypt

def get_db_connection():
    return sqlite3.connect("movies.db")

def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash the password for security
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    finally:
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_hash = result[0].encode('utf-8')
        # Check if the typed password matches the stored hash
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    return False