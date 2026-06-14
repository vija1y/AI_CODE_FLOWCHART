"""MySQL connection pool + schema bootstrap."""
import os
import mysql.connector
from mysql.connector import pooling

_pool: pooling.MySQLConnectionPool | None = None


def init_db(app):
    """Create connection pool and ensure tables exist."""
    global _pool
    cfg = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    db_name = os.getenv("DB_NAME", "ai_code_flowchart")

    # Ensure database exists
    tmp = mysql.connector.connect(**cfg)
    cur = tmp.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4")
    cur.close()
    tmp.close()

    _pool = pooling.MySQLConnectionPool(
        pool_name="ai_pool", pool_size=5, database=db_name, **cfg
    )
    _create_tables()


def get_conn():
    if _pool is None:
        raise RuntimeError("DB pool not initialized")
    return _pool.get_connection()


def _create_tables():
    schema = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(180) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS learning_sessions (
            session_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            source_code MEDIUMTEXT,
            flowchart MEDIUMTEXT,
            logic_type VARCHAR(60),
            confidence FLOAT,
            explanation MEDIUMTEXT,
            language VARCHAR(30) DEFAULT 'python',
            kind VARCHAR(30) DEFAULT 'code_to_flowchart',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """,
    ]
    conn = get_conn()
    cur = conn.cursor()
    for stmt in schema:
        cur.execute(stmt)
    conn.commit()
    cur.close()
    conn.close()
