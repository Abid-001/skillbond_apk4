"""
SkillBond - Database Layer
SQLite on-device storage for Android
"""

import sqlite3
import hashlib
import secrets
import os


def hash_password(password: str) -> str:
    """Hash a password with a random salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(stored: str, provided: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt, hashed = stored.split(":", 1)
        return hashlib.sha256((salt + provided).encode()).hexdigest() == hashed
    except Exception:
        return False


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        with self._conn() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created  DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS friends (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id  INTEGER NOT NULL,
                    name     TEXT NOT NULL,
                    phone    TEXT DEFAULT '',
                    location TEXT DEFAULT '',
                    notes    TEXT DEFAULT '',
                    created  DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS skills (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    friend_id INTEGER NOT NULL,
                    skill     TEXT NOT NULL,
                    FOREIGN KEY(friend_id) REFERENCES friends(id) ON DELETE CASCADE
                );
            """)

    # ── Auth ─────────────────────────────────────────────────────────────────

    def register(self, username: str, password: str):
        """Returns (True, user_id) or (False, error_msg)."""
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        try:
            with self._conn() as db:
                cur = db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username.strip(), hash_password(password)),
                )
                return True, cur.lastrowid
        except sqlite3.IntegrityError:
            return False, "Username already exists. Choose another."

    def login(self, username: str, password: str):
        """Returns (True, user_row) or (False, error_msg)."""
        with self._conn() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username.strip(),)
            ).fetchone()
        if user and verify_password(user["password"], password):
            return True, dict(user)
        return False, "Invalid username or password."

    # ── Friends ───────────────────────────────────────────────────────────────

    def get_friends(self, user_id: int, search="", skill="", location=""):
        """Return filtered list of friends (as dicts) for the given user."""
        query = """
            SELECT f.id, f.name, f.phone, f.location, f.notes,
                   GROUP_CONCAT(s.skill, ', ') AS skills_list
            FROM friends f
            LEFT JOIN skills s ON s.friend_id = f.id
            WHERE f.user_id = ?
        """
        params = [user_id]
        if search:
            query += " AND LOWER(f.name) LIKE ?"
            params.append(f"%{search.lower()}%")
        if skill:
            query += """ AND f.id IN (
                SELECT friend_id FROM skills WHERE LOWER(skill) LIKE ?)"""
            params.append(f"%{skill.lower()}%")
        if location:
            query += " AND LOWER(f.location) LIKE ?"
            params.append(f"%{location.lower()}%")
        query += " GROUP BY f.id ORDER BY f.name"
        with self._conn() as db:
            return [dict(r) for r in db.execute(query, params).fetchall()]

    def get_friend(self, fid: int, user_id: int):
        with self._conn() as db:
            row = db.execute(
                "SELECT * FROM friends WHERE id=? AND user_id=?", (fid, user_id)
            ).fetchone()
            return dict(row) if row else None

    def get_friend_skills(self, fid: int):
        with self._conn() as db:
            rows = db.execute(
                "SELECT skill FROM skills WHERE friend_id=? ORDER BY skill", (fid,)
            ).fetchall()
            return [r["skill"] for r in rows]

    def add_friend(self, user_id: int, name: str, phone: str,
                   location: str, notes: str, skills: list) -> int:
        with self._conn() as db:
            cur = db.execute(
                "INSERT INTO friends (user_id, name, phone, location, notes) VALUES (?,?,?,?,?)",
                (user_id, name.strip(), phone.strip(), location.strip(), notes.strip()),
            )
            fid = cur.lastrowid
            for sk in skills:
                sk = sk.strip()
                if sk:
                    db.execute(
                        "INSERT INTO skills (friend_id, skill) VALUES (?,?)", (fid, sk)
                    )
            return fid

    def update_friend(self, fid: int, name: str, phone: str,
                      location: str, notes: str, skills: list):
        with self._conn() as db:
            db.execute(
                "UPDATE friends SET name=?,phone=?,location=?,notes=? WHERE id=?",
                (name.strip(), phone.strip(), location.strip(), notes.strip(), fid),
            )
            db.execute("DELETE FROM skills WHERE friend_id=?", (fid,))
            for sk in skills:
                sk = sk.strip()
                if sk:
                    db.execute(
                        "INSERT INTO skills (friend_id, skill) VALUES (?,?)", (fid, sk)
                    )

    def delete_friend(self, fid: int):
        with self._conn() as db:
            db.execute("DELETE FROM skills WHERE friend_id=?", (fid,))
            db.execute("DELETE FROM friends WHERE id=?", (fid,))

    # ── Autocomplete helpers ──────────────────────────────────────────────────

    def get_all_skills(self, user_id: int) -> list:
        with self._conn() as db:
            rows = db.execute(
                """SELECT DISTINCT s.skill FROM skills s
                   JOIN friends f ON f.id = s.friend_id
                   WHERE f.user_id = ? ORDER BY s.skill""",
                (user_id,),
            ).fetchall()
            return [r["skill"] for r in rows]

    def get_all_locations(self, user_id: int) -> list:
        with self._conn() as db:
            rows = db.execute(
                """SELECT DISTINCT location FROM friends
                   WHERE user_id=? AND location IS NOT NULL AND location != ''
                   ORDER BY location""",
                (user_id,),
            ).fetchall()
            return [r["location"] for r in rows]

    def get_stats(self, user_id: int) -> tuple:
        """Returns (total_friends, unique_skills, unique_locations)."""
        with self._conn() as db:
            total = db.execute(
                "SELECT COUNT(*) AS c FROM friends WHERE user_id=?", (user_id,)
            ).fetchone()["c"]
            skills = db.execute(
                """SELECT COUNT(DISTINCT s.skill) AS c FROM skills s
                   JOIN friends f ON f.id=s.friend_id WHERE f.user_id=?""",
                (user_id,),
            ).fetchone()["c"]
            locs = db.execute(
                """SELECT COUNT(DISTINCT location) AS c FROM friends
                   WHERE user_id=? AND location IS NOT NULL AND location!=''""",
                (user_id,),
            ).fetchone()["c"]
            return total, skills, locs
