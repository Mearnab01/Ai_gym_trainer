import sqlite3
import streamlit as st
from pathlib import Path
from logger.logger import setup_logger

_DB_PATH = str(Path(__file__).parent.parent.parent / "data.db")
log = setup_logger()

@st.cache_resource
def _get_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        log.info(f"DB connected: {_DB_PATH}")
        return conn
    except sqlite3.Error as e:
        log.error(f"DB connection failed: {e}")
        raise


def init_db() -> None:
    conn = _get_connection()
    log.info("Initializing database...")

    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS exercises (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL REFERENCES users(id),
                exercise_name TEXT    NOT NULL,
                reps          INTEGER NOT NULL DEFAULT 0,
                sets          INTEGER NOT NULL DEFAULT 0,
                time          INTEGER NOT NULL DEFAULT 0,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_user(username: str) -> sqlite3.Row:
    conn = _get_connection()

    return conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def create_user(username: str) -> sqlite3.Row:
    conn = _get_connection()
    
    with conn:
        conn.execute(
            "INSERT INTO users (username) VALUES (?)", (username,)
        )

    return get_user(username) 


def get_or_create_user(username: str) -> sqlite3.Row:
    try:
        user = get_user(username)
        if not user:
            log.info(f"User '{username}' not found. Creating new user.")

        if user is None:
            user = create_user(username)
            log.info(f"User '{username}' created with ID {user['id']}")

        return user

    except Exception as e:
        log.error(f"Unexpected error in get_or_create_user('{username}'): {e}")
        return None


def add_exercise(user_id, exercise_name, reps, sets, time):
    log.debug(f"Adding exercise: {exercise_name} | reps={reps}, sets={sets}")

    conn = _get_connection()

    with conn:
        existing = conn.execute("""
            SELECT * FROM exercises 
            WHERE user_id = ? AND exercise_name = ? AND Date('created_at') = Date('now')
        """, (user_id, exercise_name)).fetchone()

        if existing:
            log.info(f"Updating existing exercise for user {user_id}")

            conn.execute("""
                UPDATE exercises 
                SET reps = reps + ?, sets = sets + ?, time = time + ?
                WHERE id = ?
            """, (reps, sets, time, existing['id']))

        else:
            log.info(f"Inserting new exercise for user {user_id}")

            conn.execute("""
                INSERT INTO exercises (user_id, exercise_name, sets, reps, time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, exercise_name, sets, reps, time))


def get_users_exercises(user_id):
    conn = _get_connection()

    return conn.execute("""
        SELECT * FROM exercises 
        WHERE user_id = ?
    """, (user_id,)).fetchall()