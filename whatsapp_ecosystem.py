"""
WhatsApp Ecosystem with Daily Reminders and Expense Tracking
A comprehensive Python-based system for managing WhatsApp messaging,
daily reminders, and expense tracking functionality.
"""

import json
import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import threading
import time


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class MessageType(Enum):
    """Types of messages in the WhatsApp ecosystem"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACT = "contact"


class MessageStatus(Enum):
    """Status of a message"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ExpenseCategory(Enum):
    """Categories for expense tracking"""
    FOOD = "food"
    TRANSPORT = "transport"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    OTHER = "other"


class ReminderType(Enum):
    """Types of reminders"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


# ============================================================================
# DATABASE SETUP
# ============================================================================

class Database:
    """Database manager for WhatsApp ecosystem"""

    def __init__(self, db_name: str = "whatsapp_ecosystem.db"):
        self.db_name = db_name
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database with required tables"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                phone_number TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profile_picture_url TEXT,
                status TEXT,
                last_seen TIMESTAMP
            )
        """)

        # Contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, phone_number)
            )
        """)

        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                contact_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_message_at TIMESTAMP,
                is_archived BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (contact_id) REFERENCES contacts(id)
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                media_url TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id),
                FOREIGN KEY (sender_id) REFERENCES users(id)
            )
        """)

        # Expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_method TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                reminder_type TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Reminder history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminder_history (
                id TEXT PRIMARY KEY,
                reminder_id TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'sent',
                FOREIGN KEY (reminder_id) REFERENCES reminders(id)
            )
        """)

        self.conn.commit()

    def execute(self, query: str, params: tuple = ()):
        """Execute a database query"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row"""
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows"""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# ============================================================================
# USER MANAGEMENT
# ============================================================================

class User:
    """User model for WhatsApp ecosystem"""

    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, phone_number: str, email: str, password: str) -> Dict[str, Any]:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)

        try:
            self.db.execute(
                """INSERT INTO users (id, username, phone_number, email, password_hash)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, username, phone_number, email, password_hash)
            )
            return {"success": True, "user_id": user_id, "message": "User created successfully"}
        except sqlite3.IntegrityError as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate a user"""
        password_hash = self.hash_password(password)
        user = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )

        if user:
            return {"success": True, "user_id": user[0], "message": "Authentication successful"}
        return {"success": False, "message": "Invalid credentials"}

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user details"""
        user = self.db.fetch_one(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        return dict(user) if user else None

    def update_user_status(self, user_id: str, status: str):
        """Update user online status"""
        self.db.execute(
            "UPDATE users SET status = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?",
            (status, user_id)
        )

    def add_contact(self, user_id: str, contact_name: str, phone_number: str, email: str = None) -> Dict[str, Any]:
        """Add a contact for a user"""
        contact_id = str(uuid.uuid4())

        try:
            self.db.execute(
                """INSERT INTO contacts (id, user_id, contact_name, phone_number, email)
                   VALUES (?, ?, ?, ?, ?)""",
                (contact_id, user_id, contact_name, phone_number, email)
            )
            return {"success": True, "contact_id": contact_id, "message": "Contact added"}
        except sqlite3.IntegrityError as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_contacts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all contacts for a user"""
        contacts = self.db.fetch_all(
            "SELECT * FROM contacts WHERE user_id = ?",
            (user_id,)
        )
        return [dict(contact) for contact in contacts]


# ============================================================================
# MESSAGING SYSTEM
# ============================================================================

class Message:
    """Message model for WhatsApp ecosystem"""

    def __init__(self, db: Database):
        self.db = db

    def send_message(self, sender_id: str, receiver_id: str, content: str,
                    message_type: str = MessageType.TEXT.value, media_url: str = None) -> Dict[str, Any]:
        """Send a message from sender to receiver"""
        message_id = str(uuid.uuid4())

        # Get or create conversation
        conversation = self.db.fetch_one(
            "SELECT id FROM conversations WHERE user_id = ? AND contact_id = ? LIMIT 1",
            (sender_id, receiver_id)
        )

        if not conversation:
            conversation_id = str(uuid.uuid4())
            self.db.execute(
                """INSERT INTO conversations (id, user_id, contact_id)
                   VALUES (?, ?, ?)""",
                (conversation_id, sender_id, receiver_id)
            )
        else:
            conversation_id = conversation[0]

        try:
            self.db.execute(
                """INSERT INTO messages (id, conversation_id, sender_id, message_type, content, status, media_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (message_id, conversation_id, sender_id, message_type, content, MessageStatus.SENT.value, media_url)
            )
            return {
                "success": True,
                "message_id": message_id,
                "status": MessageStatus.SENT.value,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "message": f"Error sending message: {str(e)}"}

    def update_message_status(self, message_id: str, status: str):
        """Update message delivery status"""
        self.db.execute(
            "UPDATE messages SET status = ? WHERE id = ?",
            (status, message_id)
        )

    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages from a conversation"""
        messages = self.db.fetch_all(
            """SELECT * FROM messages WHERE conversation_id = ?
               ORDER BY timestamp DESC LIMIT ?""",
            (conversation_id, limit)
        )
        return [dict(msg) for msg in messages]

    def search_messages(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Search for messages containing specific text"""
        messages = self.db.fetch_all(
            """SELECT m.* FROM messages m
               JOIN conversations c ON m.conversation_id = c.id
               WHERE c.user_id = ? AND m.content LIKE ?""",
            (user_id, f"%{query}%")
        )
        return [dict(msg) for msg in messages]


# ============================================================================
# EXPENSE TRACKING
# ============================================================================

class ExpenseTracker:
    """Expense tracking system"""

    def __init__(self, db: Database):
        self.db = db

    def add_expense(self, user_id: str, amount: float, category: str,
                   description: str = None, payment_method: str = None) -> Dict[str, Any]:
        """Add a new expense"""
        expense_id = str(uuid.uuid4())

        try:
            self.db.execute(
                """INSERT INTO expenses (id, user_id, amount, category, description, payment_method)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (expense_id, user_id, amount, category, description, payment_method)
            )
            return {
                "success": True,
                "expense_id": expense_id,
                "message": "Expense recorded successfully",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_expenses(self, user_id: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get expenses for a user within a date range"""
        if start_date and end_date:
            expenses = self.db.fetch_all(
                """SELECT * FROM expenses WHERE user_id = ? AND timestamp BETWEEN ? AND ?
                   ORDER BY timestamp DESC""",
                (user_id, start_date, end_date)
            )
        else:
            expenses = self.db.fetch_all(
                "SELECT * FROM expenses WHERE user_id = ? ORDER BY timestamp DESC",
                (user_id,)
            )
        return [dict(exp) for exp in expenses]

    def get_expenses_by_category(self, user_id: str) -> Dict[str, float]:
        """Get total expenses grouped by category"""
        categories = self.db.fetch_all(
            """SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?
               GROUP BY category""",
            (user_id,)
        )
        return {cat[0]: cat[1] for cat in categories}

    def get_daily_expenses(self, user_id: str, date: str) -> List[Dict[str, Any]]:
        """Get expenses for a specific day"""
        expenses = self.db.fetch_all(
            """SELECT * FROM expenses WHERE user_id = ? AND DATE(timestamp) = ?
               ORDER BY timestamp DESC""",
            (user_id, date)
        )
        return [dict(exp) for exp in expenses]

    def get_daily_total(self, user_id: str, date: str = None) -> float:
        """Get total expenses for a specific day"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        result = self.db.fetch_one(
            """SELECT SUM(amount) FROM expenses WHERE user_id = ? AND DATE(timestamp) = ?""",
            (user_id, date)
        )
        return result[0] if result[0] else 0.0

    def get_weekly_summary(self, user_id: str) -> Dict[str, Any]:
        """Get weekly expense summary"""
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        expenses = self.get_expenses(user_id, start_date, end_date)
        total = sum(exp["amount"] for exp in expenses)
        by_category = self.get_expenses_by_category(user_id)

        return {
            "period": f"{start_date} to {end_date}",
            "total": total,
            "count": len(expenses),
            "by_category": by_category
        }

    def get_monthly_summary(self, user_id: str, month: int = None, year: int = None) -> Dict[str, Any]:
        """Get monthly expense summary"""
        if not month:
            month = datetime.now().month
        if not year:
            year = datetime.now().year

        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        expenses = self.db.fetch_all(
            """SELECT * FROM expenses WHERE user_id = ? AND timestamp >= ? AND timestamp < ?
               ORDER BY timestamp DESC""",
            (user_id, start_date, end_date)
        )
        expenses = [dict(exp) for exp in expenses]
        total = sum(exp["amount"] for exp in expenses)

        by_category = {}
        for exp in expenses:
            cat = exp["category"]
            by_category[cat] = by_category.get(cat, 0) + exp["amount"]

        return {
            "period": f"{year}-{month:02d}",
            "total": total,
            "count": len(expenses),
            "by_category": by_category
        }


# ============================================================================
# REMINDER SYSTEM
# ============================================================================

class ReminderManager:
    """Daily reminders and notification system"""

    def __init__(self, db: Database):
        self.db = db
        self.active_reminders = {}
        self.reminder_thread = None
        self.running = False

    def create_reminder(self, user_id: str, title: str, description: str,
                       reminder_type: str, scheduled_time: str) -> Dict[str, Any]:
        """Create a new reminder"""
        reminder_id = str(uuid.uuid4())

        try:
            self.db.execute(
                """INSERT INTO reminders (id, user_id, title, description, reminder_type, scheduled_time)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (reminder_id, user_id, title, description, reminder_type, scheduled_time)
            )
            return {
                "success": True,
                "reminder_id": reminder_id,
                "message": "Reminder created successfully"
            }
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all reminders for a user"""
        reminders = self.db.fetch_all(
            "SELECT * FROM reminders WHERE user_id = ? AND is_active = 1",
            (user_id,)
        )
        return [dict(rem) for rem in reminders]

    def delete_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """Delete/deactivate a reminder"""
        self.db.execute(
            "UPDATE reminders SET is_active = 0 WHERE id = ?",
            (reminder_id,)
        )
        return {"success": True, "message": "Reminder deleted"}

    def send_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """Send/trigger a reminder"""
        reminder = self.db.fetch_one(
            "SELECT * FROM reminders WHERE id = ?",
            (reminder_id,)
        )

        if not reminder:
            return {"success": False, "message": "Reminder not found"}

        history_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO reminder_history (id, reminder_id, status)
               VALUES (?, ?, ?)""",
            (history_id, reminder_id, "sent")
        )

        return {
            "success": True,
            "reminder_id": reminder_id,
            "title": reminder[2],
            "description": reminder[3],
            "timestamp": datetime.now().isoformat()
        }

    def start_reminder_scheduler(self):
        """Start the reminder scheduler in a background thread"""
        if self.running:
            return {"message": "Reminder scheduler already running"}

        self.running = True
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
        return {"success": True, "message": "Reminder scheduler started"}

    def _reminder_loop(self):
        """Background loop to check and send reminders"""
        while self.running:
            try:
                reminders = self.db.fetch_all(
                    "SELECT * FROM reminders WHERE is_active = 1"
                )

                for reminder in reminders:
                    scheduled_time = datetime.fromisoformat(reminder[5])
                    now = datetime.now()

                    if now >= scheduled_time and (now - scheduled_time).total_seconds() < 60:
                        self.send_reminder(reminder[0])

                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in reminder loop: {str(e)}")
                time.sleep(10)

    def stop_reminder_scheduler(self):
        """Stop the reminder scheduler"""
        self.running = False
        return {"success": True, "message": "Reminder scheduler stopped"}


# ============================================================================
# DAILY REMINDER SERVICE
# ============================================================================

class DailyReminderService:
    """Service for creating and managing daily reminders (e.g., expense tracking, check-ins)"""

    def __init__(self, db: Database, reminder_manager: ReminderManager):
        self.db = db
        self.reminder_manager = reminder_manager

    def create_daily_expense_reminder(self, user_id: str, hour: int = 20, minute: int = 0) -> Dict[str, Any]:
        """Create a daily reminder to track expenses"""
        time_str = f"{hour:02d}:{minute:02d}"
        scheduled_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

        if scheduled_time < datetime.now():
            scheduled_time += timedelta(days=1)

        return self.reminder_manager.create_reminder(
            user_id,
            "Daily Expense Tracker",
            "Time to log your expenses for today!",
            ReminderType.DAILY.value,
            scheduled_time.isoformat()
        )

    def create_daily_check_in_reminder(self, user_id: str, hour: int = 9, minute: int = 0) -> Dict[str, Any]:
        """Create a daily check-in reminder"""
        scheduled_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

        if scheduled_time < datetime.now():
            scheduled_time += timedelta(days=1)

        return self.reminder_manager.create_reminder(
            user_id,
            "Daily Check-in",
            "Have you logged your expenses today?",
            ReminderType.DAILY.value,
            scheduled_time.isoformat()
        )

    def create_weekly_summary_reminder(self, user_id: str, day_of_week: int = 0, hour: int = 18) -> Dict[str, Any]:
        """Create a weekly summary reminder (0=Monday, 6=Sunday)"""
        now = datetime.now()
        days_ahead = day_of_week - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        scheduled_time = now + timedelta(days=days_ahead)
        scheduled_time = scheduled_time.replace(hour=hour, minute=0, second=0, microsecond=0)

        return self.reminder_manager.create_reminder(
            user_id,
            "Weekly Expense Summary",
            "Check your weekly spending summary",
            ReminderType.WEEKLY.value,
            scheduled_time.isoformat()
        )


# ============================================================================
# WHATSAPP ECOSYSTEM MAIN CONTROLLER
# ============================================================================

class WhatsAppEcosystem:
    """Main controller for the WhatsApp ecosystem"""

    def __init__(self, db_name: str = "whatsapp_ecosystem.db"):
        self.db = Database(db_name)
        self.user = User(self.db)
        self.message = Message(self.db)
        self.expense_tracker = ExpenseTracker(self.db)
        self.reminder_manager = ReminderManager(self.db)
        self.daily_reminder_service = DailyReminderService(self.db, self.reminder_manager)
        self.current_user_id = None

    # User Management
    def register(self, username: str, phone_number: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        return self.user.create_user(username, phone_number, email, password)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login a user"""
        result = self.user.authenticate_user(username, password)
        if result["success"]:
            self.current_user_id = result["user_id"]
            self.user.update_user_status(self.current_user_id, "online")
        return result

    def logout(self) -> Dict[str, Any]:
        """Logout current user"""
        if self.current_user_id:
            self.user.update_user_status(self.current_user_id, "offline")
            self.current_user_id = None
            return {"success": True, "message": "Logged out successfully"}
        return {"success": False, "message": "No user logged in"}

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """Get current user profile"""
        if self.current_user_id:
            return self.user.get_user(self.current_user_id)
        return None

    def add_contact(self, contact_name: str, phone_number: str, email: str = None) -> Dict[str, Any]:
        """Add a contact"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.user.add_contact(self.current_user_id, contact_name, phone_number, email)

    def list_contacts(self) -> List[Dict[str, Any]]:
        """List all contacts"""
        if not self.current_user_id:
            return []
        return self.user.get_contacts(self.current_user_id)

    # Messaging
    def send_message(self, receiver_id: str, content: str, message_type: str = MessageType.TEXT.value) -> Dict[str, Any]:
        """Send a message"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.message.send_message(self.current_user_id, receiver_id, content, message_type)

    def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation messages"""
        if not self.current_user_id:
            return []
        return self.message.get_conversation_messages(conversation_id)

    def search_messages(self, query: str) -> List[Dict[str, Any]]:
        """Search messages"""
        if not self.current_user_id:
            return []
        return self.message.search_messages(self.current_user_id, query)

    # Expense Tracking
    def log_expense(self, amount: float, category: str, description: str = None,
                   payment_method: str = None) -> Dict[str, Any]:
        """Log an expense"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.expense_tracker.add_expense(
            self.current_user_id, amount, category, description, payment_method
        )

    def get_expenses(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get expenses"""
        if not self.current_user_id:
            return []
        return self.expense_tracker.get_expenses(self.current_user_id, start_date, end_date)

    def get_daily_expenses(self, date: str = None) -> List[Dict[str, Any]]:
        """Get daily expenses"""
        if not self.current_user_id:
            return []
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.expense_tracker.get_daily_expenses(self.current_user_id, date)

    def get_daily_total(self, date: str = None) -> float:
        """Get daily expense total"""
        if not self.current_user_id:
            return 0.0
        return self.expense_tracker.get_daily_total(self.current_user_id, date)

    def get_weekly_summary(self) -> Dict[str, Any]:
        """Get weekly expense summary"""
        if not self.current_user_id:
            return {}
        return self.expense_tracker.get_weekly_summary(self.current_user_id)

    def get_monthly_summary(self, month: int = None, year: int = None) -> Dict[str, Any]:
        """Get monthly expense summary"""
        if not self.current_user_id:
            return {}
        return self.expense_tracker.get_monthly_summary(self.current_user_id, month, year)

    def get_expenses_by_category(self) -> Dict[str, float]:
        """Get expenses grouped by category"""
        if not self.current_user_id:
            return {}
        return self.expense_tracker.get_expenses_by_category(self.current_user_id)

    # Reminders
    def create_reminder(self, title: str, description: str, reminder_type: str, scheduled_time: str) -> Dict[str, Any]:
        """Create a reminder"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.reminder_manager.create_reminder(
            self.current_user_id, title, description, reminder_type, scheduled_time
        )

    def get_reminders(self) -> List[Dict[str, Any]]:
        """Get all active reminders"""
        if not self.current_user_id:
            return []
        return self.reminder_manager.get_reminders(self.current_user_id)

    def delete_reminder(self, reminder_id: str) -> Dict[str, Any]:
        """Delete a reminder"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.reminder_manager.delete_reminder(reminder_id)

    # Daily Reminders
    def setup_daily_expense_reminder(self, hour: int = 20, minute: int = 0) -> Dict[str, Any]:
        """Setup daily expense tracking reminder"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.daily_reminder_service.create_daily_expense_reminder(
            self.current_user_id, hour, minute
        )

    def setup_daily_check_in_reminder(self, hour: int = 9, minute: int = 0) -> Dict[str, Any]:
        """Setup daily check-in reminder"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.daily_reminder_service.create_daily_check_in_reminder(
            self.current_user_id, hour, minute
        )

    def setup_weekly_summary_reminder(self, day_of_week: int = 0, hour: int = 18) -> Dict[str, Any]:
        """Setup weekly summary reminder"""
        if not self.current_user_id:
            return {"success": False, "message": "User not logged in"}
        return self.daily_reminder_service.create_weekly_summary_reminder(
            self.current_user_id, day_of_week, hour
        )

    # Reminder Scheduler Control
    def start_reminders(self) -> Dict[str, Any]:
        """Start the reminder scheduler"""
        return self.reminder_manager.start_reminder_scheduler()

    def stop_reminders(self) -> Dict[str, Any]:
        """Stop the reminder scheduler"""
        return self.reminder_manager.stop_reminder_scheduler()

    # Database Management
    def close(self):
        """Close database connection"""
        self.stop_reminders()
        self.db.close()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Example usage of WhatsApp ecosystem"""
    print("=" * 70)
    print("WhatsApp Ecosystem with Daily Reminders and Expense Tracking")
    print("=" * 70)

    # Initialize ecosystem
    app = WhatsAppEcosystem()
    app.start_reminders()

    # User Registration
    print("\n[1] USER REGISTRATION")
    print("-" * 70)
    reg_result = app.register("john_doe", "+1234567890", "john@example.com", "password123")
    print(f"Registration: {reg_result}")

    reg_result2 = app.register("jane_smith", "+0987654321", "jane@example.com", "password456")
    print(f"Registration: {reg_result2}")

    # User Login
    print("\n[2] USER LOGIN")
    print("-" * 70)
    login_result = app.login("john_doe", "password123")
    print(f"Login: {login_result}")

    # Add Contacts
    print("\n[3] ADD CONTACTS")
    print("-" * 70)
    app.add_contact("Jane Smith", "+0987654321", "jane@example.com")
    print("Contact added successfully")

    # Send Messages
    print("\n[4] SEND MESSAGES")
    print("-" * 70)
    msg_result = app.send_message("jane_contact_id", "Hi Jane! How are you?")
    print(f"Message sent: {msg_result}")

    # Log Expenses
    print("\n[5] LOG EXPENSES")
    print("-" * 70)
    app.log_expense(50.0, ExpenseCategory.FOOD.value, "Lunch at restaurant")
    print("Expense logged: $50 - Food")

    app.log_expense(25.0, ExpenseCategory.TRANSPORT.value, "Uber ride")
    print("Expense logged: $25 - Transport")

    app.log_expense(15.0, ExpenseCategory.ENTERTAINMENT.value, "Movie ticket")
    print("Expense logged: $15 - Entertainment")

    # View Daily Expenses
    print("\n[6] VIEW DAILY EXPENSES")
    print("-" * 70)
    daily_expenses = app.get_daily_expenses()
    print(f"Daily Expenses: {len(daily_expenses)} transactions")
    daily_total = app.get_daily_total()
    print(f"Daily Total: ${daily_total:.2f}")

    # View Expenses by Category
    print("\n[7] EXPENSES BY CATEGORY")
    print("-" * 70)
    by_category = app.get_expenses_by_category()
    for category, amount in by_category.items():
        print(f"  {category.upper()}: ${amount:.2f}")

    # Weekly Summary
    print("\n[8] WEEKLY SUMMARY")
    print("-" * 70)
    weekly = app.get_weekly_summary()
    print(f"Period: {weekly.get('period')}")
    print(f"Total: ${weekly.get('total', 0):.2f}")
    print(f"Transactions: {weekly.get('count', 0)}")

    # Setup Daily Reminders
    print("\n[9] SETUP DAILY REMINDERS")
    print("-" * 70)
    reminder1 = app.setup_daily_expense_reminder(hour=20, minute=0)
    print(f"Daily expense reminder: {reminder1}")

    reminder2 = app.setup_daily_check_in_reminder(hour=9, minute=0)
    print(f"Daily check-in reminder: {reminder2}")

    reminder3 = app.setup_weekly_summary_reminder(day_of_week=0, hour=18)
    print(f"Weekly summary reminder: {reminder3}")

    # View Active Reminders
    print("\n[10] ACTIVE REMINDERS")
    print("-" * 70)
    reminders = app.get_reminders()
    for reminder in reminders:
        print(f"  • {reminder[2]} - {reminder[3]}")

    # User Profile
    print("\n[11] USER PROFILE")
    print("-" * 70)
    profile = app.get_profile()
    if profile:
        print(f"Username: {profile.get('username')}")
        print(f"Email: {profile.get('email')}")
        print(f"Phone: {profile.get('phone_number')}")
        print(f"Status: {profile.get('status')}")

    # Logout
    print("\n[12] LOGOUT")
    print("-" * 70)
    logout_result = app.logout()
    print(f"Logout: {logout_result}")

    # Close ecosystem
    app.close()
    print("\n" + "=" * 70)
    print("WhatsApp Ecosystem closed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
