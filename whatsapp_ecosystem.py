"""Minimal WhatsApp ecosystem domain and webhook helpers.

The module deliberately uses only the Python standard library so the core can be
run and tested before choosing a web framework or WhatsApp SDK.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Any, Optional


class WhatsAppEcosystem:
    """SQLite-backed users and expense tracking used by the starter project."""

    def __init__(self, db_path: str = "whatsapp_ecosystem.db") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._current_user_id: Optional[str] = None
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                phone_number TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                status TEXT,
                last_seen TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS expenses (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                category TEXT NOT NULL,
                description TEXT,
                payment_method TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        self.conn.commit()

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register(self, username: str, phone_number: str, email: str, password: str) -> Optional[str]:
        user_id = str(uuid.uuid4())
        try:
            self.conn.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, username, phone_number, email, self._hash_password(password),
                 "offline", None, datetime.now(timezone.utc).isoformat()),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            return None
        return user_id

    def login(self, username: str, password: str) -> bool:
        row = self.conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
        if row is None or not hmac.compare_digest(row["password_hash"], self._hash_password(password)):
            return False
        self._current_user_id = row["id"]
        self.conn.execute(
            "UPDATE users SET status = 'online', last_seen = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), self._current_user_id),
        )
        self.conn.commit()
        return True

    def logout(self) -> None:
        if self._current_user_id:
            self.conn.execute("UPDATE users SET status = 'offline' WHERE id = ?", (self._current_user_id,))
            self.conn.commit()
        self._current_user_id = None

    def current_profile(self) -> Optional[dict[str, Any]]:
        if not self._current_user_id:
            return None
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (self._current_user_id,)).fetchone()
        return dict(row) if row else None

    def log_expense(self, amount: float, category: str, description: str = "", payment_method: Optional[str] = None) -> str:
        if not self._current_user_id:
            raise RuntimeError("No user logged in")
        if amount < 0:
            raise ValueError("amount must be non-negative")
        expense_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?, ?)",
            (expense_id, self._current_user_id, amount, category, description, payment_method,
             datetime.now(timezone.utc).isoformat()),
        )
        self.conn.commit()
        return expense_id

    def get_weekly_summary(self) -> list[dict[str, Any]]:
        if not self._current_user_id:
            return []
        since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        rows = self.conn.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE user_id = ? AND timestamp >= ? GROUP BY category",
            (self._current_user_id, since),
        ).fetchall()
        return [dict(row) for row in rows]

    def close(self) -> None:
        self.conn.close()


class WhatsAppWebhook:
    """Framework-neutral webhook verification and payload normalization."""

    def __init__(self, verify_token: str, app_secret: str | None = None) -> None:
        self.verify_token = verify_token
        self.app_secret = app_secret

    def verify_challenge(self, mode: str, token: str, challenge: str) -> tuple[int, str]:
        if mode == "subscribe" and secrets.compare_digest(token, self.verify_token):
            return HTTPStatus.OK, challenge
        return HTTPStatus.FORBIDDEN, "verification failed"

    def verify_signature(self, body: bytes, signature: str | None) -> bool:
        if not self.app_secret:
            return True
        if not signature or not signature.startswith("sha256="):
            return False
        expected = hmac.new(self.app_secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature[7:], expected)

    @staticmethod
    def parse_event(body: bytes) -> list[dict[str, Any]]:
        payload = json.loads(body)
        messages: list[dict[str, Any]] = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages.extend(value.get("messages", []))
        return messages


def main() -> int:
    print("WhatsApp ecosystem scaffold ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
