"""
Pytest tests for WhatsApp Ecosystem SaaS
Tests cover user management, messaging, expenses, and reminders
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta

# Import the ecosystem
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from whatsapp_ecosystem import (
    WhatsAppEcosystem,
    Database,
    User,
    Message,
    ExpenseTracker,
    ReminderManager,
    ExpenseCategory,
    MessageType,
    ReminderType,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def ecosystem(temp_db):
    """Create a WhatsApp ecosystem instance with temp database"""
    app = WhatsAppEcosystem(db_name=temp_db)
    yield app
    app.close()


# ============================================================================
# USER MANAGEMENT TESTS
# ============================================================================


class TestUserManagement:
    """Test user registration, login, and profile management"""

    def test_user_registration_success(self, ecosystem):
        """Test successful user registration"""
        result = ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        assert result["success"] is True
        assert "user_id" in result

    def test_user_registration_duplicate_username(self, ecosystem):
        """Test that duplicate usernames are rejected"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        result = ecosystem.register(
            "john_doe", "+0987654321", "john2@example.com", "password456"
        )
        assert result["success"] is False

    def test_user_login_success(self, ecosystem):
        """Test successful user login"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        result = ecosystem.login("john_doe", "password123")
        assert result["success"] is True
        assert "user_id" in result

    def test_user_login_invalid_credentials(self, ecosystem):
        """Test login with invalid credentials"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        result = ecosystem.login("john_doe", "wrongpassword")
        assert result["success"] is False

    def test_user_logout(self, ecosystem):
        """Test user logout"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        result = ecosystem.logout()
        assert result["success"] is True
        assert ecosystem.current_user_id is None

    def test_get_user_profile(self, ecosystem):
        """Test retrieving user profile"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        profile = ecosystem.get_profile()
        assert profile is not None
        assert profile["username"] == "john_doe"
        assert profile["email"] == "john@example.com"
        assert profile["phone_number"] == "+1234567890"


# ============================================================================
# CONTACT MANAGEMENT TESTS
# ============================================================================


class TestContactManagement:
    """Test contact addition and listing"""

    def test_add_contact(self, ecosystem):
        """Test adding a contact"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        result = ecosystem.add_contact("Jane Smith", "+0987654321", "jane@example.com")
        assert result["success"] is True
        assert "contact_id" in result

    def test_add_contact_without_login(self, ecosystem):
        """Test adding a contact without logging in"""
        result = ecosystem.add_contact("Jane Smith", "+0987654321", "jane@example.com")
        assert result["success"] is False

    def test_list_contacts(self, ecosystem):
        """Test listing contacts"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        ecosystem.add_contact("Jane Smith", "+0987654321", "jane@example.com")
        ecosystem.add_contact("Bob Johnson", "+1111111111", "bob@example.com")
        contacts = ecosystem.list_contacts()
        assert len(contacts) == 2
        assert contacts[0]["contact_name"] == "Jane Smith"

    def test_list_contacts_empty(self, ecosystem):
        """Test listing contacts when none exist"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        contacts = ecosystem.list_contacts()
        assert len(contacts) == 0


# ============================================================================
# EXPENSE TRACKING TESTS
# ============================================================================


class TestExpenseTracking:
    """Test expense logging and retrieval"""

    def test_log_expense(self, ecosystem):
        """Test logging a single expense"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        result = ecosystem.log_expense(
            50.0, ExpenseCategory.FOOD.value, "Lunch at restaurant"
        )
        assert result["success"] is True
        assert "expense_id" in result

    def test_log_multiple_expenses(self, ecosystem):
        """Test logging multiple expenses"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        ecosystem.log_expense(50.0, ExpenseCategory.FOOD.value, "Lunch")
        ecosystem.log_expense(25.0, ExpenseCategory.TRANSPORT.value, "Uber")
        ecosystem.log_expense(15.0, ExpenseCategory.ENTERTAINMENT.value, "Movie")
        expenses = ecosystem.get_expenses()
        assert len(expenses) == 3

    def test_get_daily_expenses(self, ecosystem):
        """Test retrieving daily expenses"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        ecosystem.log_expense(50.0, ExpenseCategory.FOOD.value, "Lunch")
        ecosystem.log_expense(25.0, ExpenseCategory.TRANSPORT.value, "Uber")
        today = datetime.now().strftime("%Y-%m-%d")
        expenses = ecosystem.get_daily_expenses(today)
        assert len(expenses) == 2

    def test_get_daily_total(self, ecosystem):
        """Test calculating daily total"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        ecosystem.log_expense(50.0, ExpenseCategory.FOOD.value)
        ecosystem.log_expense(25.0, ExpenseCategory.TRANSPORT.value)
        total = ecosystem.get_daily_total()
        assert total == 75.0

    def test_get_expenses_by_category(self, ecosystem):
        """Test retrieving expenses grouped by category"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        ecosystem.log_expense(50.0, ExpenseCategory.FOOD.value)
        ecosystem.log_expense(30.0, ExpenseCategory.FOOD.value)
        ecosystem.log_expense(25.0, ExpenseCategory.TRANSPORT.value)
        by_category = ecosystem.get_expenses_by_category()
        assert by_category[ExpenseCategory.FOOD.value] == 80.0
        assert by_category[ExpenseCategory.TRANSPORT.value] == 25.0

    def test_weekly_summary(self, ecosystem):
        """Test weekly expense summary"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        ecosystem.log_expense(50.0, ExpenseCategory.FOOD.value)
        ecosystem.log_expense(25.0, ExpenseCategory.TRANSPORT.value)
        summary = ecosystem.get_weekly_summary()
        assert summary["total"] == 75.0
        assert summary["count"] == 2
        assert "by_category" in summary

    def test_monthly_summary(self, ecosystem):
        """Test monthly expense summary"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        ecosystem.log_expense(100.0, ExpenseCategory.UTILITIES.value)
        ecosystem.log_expense(50.0, ExpenseCategory.HEALTHCARE.value)
        summary = ecosystem.get_monthly_summary()
        assert summary["total"] == 150.0
        assert summary["count"] == 2


# ============================================================================
# REMINDER TESTS
# ============================================================================


class TestReminders:
    """Test reminder creation and management"""

    def test_create_reminder(self, ecosystem):
        """Test creating a reminder"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        scheduled_time = (datetime.now() + timedelta(hours=1)).isoformat()
        result = ecosystem.create_reminder(
            "Buy groceries", "Remember to buy milk", ReminderType.DAILY.value, scheduled_time
        )
        assert result["success"] is True
        assert "reminder_id" in result

    def test_get_reminders(self, ecosystem):
        """Test retrieving active reminders"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        scheduled_time = (datetime.now() + timedelta(hours=1)).isoformat()
        ecosystem.create_reminder(
            "Task 1", "Description 1", ReminderType.DAILY.value, scheduled_time
        )
        ecosystem.create_reminder(
            "Task 2", "Description 2", ReminderType.WEEKLY.value, scheduled_time
        )
        reminders = ecosystem.get_reminders()
        assert len(reminders) == 2

    def test_delete_reminder(self, ecosystem):
        """Test deleting a reminder"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        scheduled_time = (datetime.now() + timedelta(hours=1)).isoformat()
        reminder_result = ecosystem.create_reminder(
            "Task", "Description", ReminderType.DAILY.value, scheduled_time
        )
        reminder_id = reminder_result["reminder_id"]
        result = ecosystem.delete_reminder(reminder_id)
        assert result["success"] is True
        reminders = ecosystem.get_reminders()
        assert len(reminders) == 0

    def test_setup_daily_expense_reminder(self, ecosystem):
        """Test setting up daily expense reminder"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        result = ecosystem.setup_daily_expense_reminder(hour=20, minute=0)
        assert result["success"] is True

    def test_setup_daily_checkin_reminder(self, ecosystem):
        """Test setting up daily check-in reminder"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        result = ecosystem.setup_daily_check_in_reminder(hour=9, minute=0)
        assert result["success"] is True

    def test_setup_weekly_summary_reminder(self, ecosystem):
        """Test setting up weekly summary reminder"""
        ecosystem.register(
            "john_doe", "+1234567890", "john@example.com", "password123"
        )
        ecosystem.login("john_doe", "password123")
        result = ecosystem.setup_weekly_summary_reminder(day_of_week=0, hour=18)
        assert result["success"] is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """End-to-end integration tests"""

    def test_full_user_workflow(self, ecosystem):
        """Test a complete user workflow"""
        # Register
        ecosystem.register(
            "alice", "+1111111111", "alice@example.com", "password123"
        )

        # Login
        ecosystem.login("alice", "password123")
        assert ecosystem.current_user_id is not None

        # Add contact
        ecosystem.add_contact("Bob", "+2222222222", "bob@example.com")
        contacts = ecosystem.list_contacts()
        assert len(contacts) == 1

        # Log expenses
        ecosystem.log_expense(50.0, ExpenseCategory.FOOD.value, "Breakfast")
        ecosystem.log_expense(25.0, ExpenseCategory.TRANSPORT.value, "Bus")

        # Setup reminders
        ecosystem.setup_daily_expense_reminder(20, 0)
        reminders = ecosystem.get_reminders()
        assert len(reminders) >= 1

        # Get summary
        summary = ecosystem.get_weekly_summary()
        assert summary["total"] == 75.0

        # Logout
        ecosystem.logout()
        assert ecosystem.current_user_id is None

    def test_multiple_users_isolated_data(self, ecosystem):
        """Test that multiple users have isolated data"""
        # User 1
        ecosystem.register("user1", "+1111111111", "user1@example.com", "pass1")
        ecosystem.login("user1", "pass1")
        ecosystem.log_expense(100.0, ExpenseCategory.FOOD.value)
        user1_total = ecosystem.get_daily_total()
        ecosystem.logout()

        # User 2
        ecosystem.register("user2", "+2222222222", "user2@example.com", "pass2")
        ecosystem.login("user2", "pass2")
        ecosystem.log_expense(50.0, ExpenseCategory.TRANSPORT.value)
        user2_total = ecosystem.get_daily_total()
        ecosystem.logout()

        # Verify isolation
        assert user1_total == 100.0
        assert user2_total == 50.0
