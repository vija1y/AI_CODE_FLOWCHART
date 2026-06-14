"""User DB helpers."""
import bcrypt
from database.db import get_conn


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def check_password(pw: str, pw_hash: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), pw_hash.encode())
    except Exception:
        return False


def create_user(username: str, email: str, password: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
        (username, email, hash_password(password)),
    )
    conn.commit()
    uid = cur.lastrowid
    cur.close()
    conn.close()
    return uid


def get_user_by_email(email: str):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def get_user_by_id(uid: int):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, email, created_at FROM users WHERE id=%s", (uid,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row
