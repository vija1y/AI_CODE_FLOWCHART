"""Learning session DB helpers."""
from database.db import get_conn


def save_session(user_id, source_code=None, flowchart=None, logic_type=None,
                 confidence=None, explanation=None, language="python",
                 kind="code_to_flowchart"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO learning_sessions
           (user_id, source_code, flowchart, logic_type, confidence,
            explanation, language, kind)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        (user_id, source_code, flowchart, logic_type, confidence,
         explanation, language, kind),
    )
    conn.commit()
    sid = cur.lastrowid
    cur.close()
    conn.close()
    return sid


def list_sessions(user_id, limit=100):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT * FROM learning_sessions WHERE user_id=%s
           ORDER BY created_at DESC LIMIT %s""",
        (user_id, limit),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def delete_session(user_id, session_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM learning_sessions WHERE session_id=%s AND user_id=%s",
        (session_id, user_id),
    )
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    return affected
