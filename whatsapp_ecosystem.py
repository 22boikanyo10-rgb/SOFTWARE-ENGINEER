import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class WhatsAppEcosystem:
    def __init__(self, db_path: str = "whatsapp_ecosystem.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()
        self._current_user_id: Optional[str] = None

    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                phone_number TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                status TEXT,
                last_seen TIMESTAMP,
                created_at TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                payment_method TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        self.conn.commit()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register(self, username: str, phone_number: str, email: str, password: str) -> Optional[str]:
        uid = str(uuid.uuid4())
        password_hash = self._hash_password(password)
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (id, username, phone_number, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (uid, username, phone_number, email, password_hash, datetime.utcnow()),
            )
            self.conn.commit()
            return uid
        except sqlite3.IntegrityError:
            return None

    def login(self, username: str, password: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            return False
        if row["password_hash"] != self._hash_password(password):
            return False
        self._current_user_id = row["id"]
        cur.execute("UPDATE users SET last_seen = ? WHERE id = ?", (datetime.utcnow(), self._current_user_id))
        self.conn.commit()
        return True

    def logout(self):
        self._current_user_id = None

    def current_profile(self) -> Optional[Dict]:
        if not self._current_user_id:
            return None
        cur = self.conn.cursor()
        cur.execute("SELECT id, username, phone_number, email, status, last_seen, created_at FROM users WHERE id = ?", (self._current_user_id,))
        row = cur.fetchone()
        if not row:
            return None
        return dict(row)

    def log_expense(self, amount: float, category: str, description: str = "", payment_method: Optional[str] = None) -> str:
        if not self._current_user_id:
            raise RuntimeError("No user logged in")
        eid = str(uuid.uuid4())
        ts = datetime.utcnow()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO expenses (id, user_id, amount, category, description, payment_method, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (eid, self._current_user_id, amount, category, description, payment_method, ts),
        )
        self.conn.commit()
        return eid

    def get_weekly_summary(self) -> List[Dict]:
        if not self._current_user_id:
            return []
        since = datetime.utcnow() - timedelta(days=7)
        cur = self.conn.cursor()
        cur.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? AND timestamp >= ? GROUP BY category",
            (self._current_user_id, since),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def start_reminders(self):
        # Stub: a real implementation would spawn a scheduler or background thread
        print("Reminder scheduler started (stub)")

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    app = WhatsAppEcosystem()
    print("Created DB at", app.db_path)
    app.close()
