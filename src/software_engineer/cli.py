"""
CLI interface for WhatsApp Ecosystem SaaS
Provides command-line access to user management, messaging, expenses, and reminders
"""

import sys
import os
from datetime import datetime
from typing import Optional

# Add project root to path to import whatsapp_ecosystem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from whatsapp_ecosystem import (
    WhatsAppEcosystem,
    ExpenseCategory,
    ReminderType,
)


class WhatsAppCLI:
    """Command-line interface for WhatsApp Ecosystem"""

    def __init__(self):
        self.app = WhatsAppEcosystem()
        self.app.start_reminders()

    def register(self, username: str, phone_number: str, email: str, password: str):
        """Register a new user"""
        result = self.app.register(username, phone_number, email, password)
        if result["success"]:
            print(f"✓ Registration successful. User ID: {result['user_id']}")
        else:
            print(f"✗ Registration failed: {result['message']}")
        return result

    def login(self, username: str, password: str):
        """Login a user"""
        result = self.app.login(username, password)
        if result["success"]:
            print(f"✓ Logged in as {username}")
        else:
            print(f"✗ Login failed: {result['message']}")
        return result

    def logout(self):
        """Logout current user"""
        result = self.app.logout()
        if result["success"]:
            print("✓ Logged out successfully")
        else:
            print(f"✗ Logout failed: {result['message']}")
        return result

    def profile(self):
        """Display current user profile"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        profile = self.app.get_profile()
        if profile:
            print("\n" + "=" * 50)
            print("USER PROFILE")
            print("=" * 50)
            print(f"Username:  {profile.get('username')}")
            print(f"Email:     {profile.get('email')}")
            print(f"Phone:     {profile.get('phone_number')}")
            print(f"Status:    {profile.get('status')}")
            print(f"Created:   {profile.get('created_at')}")
            print("=" * 50 + "\n")
        else:
            print("✗ Could not retrieve profile")

    def add_contact(self, contact_name: str, phone_number: str, email: Optional[str] = None):
        """Add a contact"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        result = self.app.add_contact(contact_name, phone_number, email)
        if result["success"]:
            print(f"✓ Contact '{contact_name}' added. ID: {result['contact_id']}")
        else:
            print(f"✗ Failed to add contact: {result['message']}")
        return result

    def list_contacts(self):
        """List all contacts"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        contacts = self.app.list_contacts()
        if not contacts:
            print("No contacts found")
            return

        print("\n" + "=" * 60)
        print("CONTACTS")
        print("=" * 60)
        for idx, contact in enumerate(contacts, 1):
            print(f"{idx}. {contact.get('contact_name')}")
            print(f"   Phone: {contact.get('phone_number')}")
            if contact.get('email'):
                print(f"   Email: {contact.get('email')}")
        print("=" * 60 + "\n")

    def log_expense(
        self,
        amount: float,
        category: str,
        description: Optional[str] = None,
        payment_method: Optional[str] = None,
    ):
        """Log an expense"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        # Validate category
        valid_categories = [c.value for c in ExpenseCategory]
        if category not in valid_categories:
            print(f"✗ Invalid category. Valid options: {', '.join(valid_categories)}")
            return

        result = self.app.log_expense(amount, category, description, payment_method)
        if result["success"]:
            print(f"✓ Expense logged: ${amount:.2f} ({category.upper()})")
            if description:
                print(f"  Note: {description}")
        else:
            print(f"✗ Failed to log expense: {result['message']}")
        return result

    def view_daily_expenses(self, date: Optional[str] = None):
        """View daily expenses"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        expenses = self.app.get_daily_expenses(date)
        total = self.app.get_daily_total(date)

        print("\n" + "=" * 70)
        print(f"DAILY EXPENSES - {date}")
        print("=" * 70)
        if not expenses:
            print("No expenses recorded for this date")
        else:
            for idx, exp in enumerate(expenses, 1):
                print(f"{idx}. ${exp.get('amount', 0):.2f} - {exp.get('category').upper()}")
                if exp.get('description'):
                    print(f"   {exp.get('description')}")
        print("-" * 70)
        print(f"TOTAL: ${total:.2f}")
        print("=" * 70 + "\n")

    def view_weekly_summary(self):
        """View weekly expense summary"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        summary = self.app.get_weekly_summary()

        print("\n" + "=" * 70)
        print("WEEKLY EXPENSE SUMMARY")
        print("=" * 70)
        print(f"Period: {summary.get('period')}")
        print(f"Total:  ${summary.get('total', 0):.2f}")
        print(f"Transactions: {summary.get('count', 0)}")
        print("\nBy Category:")
        by_cat = summary.get('by_category', {})
        if by_cat:
            for category, amount in by_cat.items():
                print(f"  {category.upper()}: ${amount:.2f}")
        print("=" * 70 + "\n")

    def view_monthly_summary(self, month: Optional[int] = None, year: Optional[int] = None):
        """View monthly expense summary"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        summary = self.app.get_monthly_summary(month, year)

        print("\n" + "=" * 70)
        print("MONTHLY EXPENSE SUMMARY")
        print("=" * 70)
        print(f"Period: {summary.get('period')}")
        print(f"Total:  ${summary.get('total', 0):.2f}")
        print(f"Transactions: {summary.get('count', 0)}")
        print("\nBy Category:")
        by_cat = summary.get('by_category', {})
        if by_cat:
            for category, amount in by_cat.items():
                print(f"  {category.upper()}: ${amount:.2f}")
        print("=" * 70 + "\n")

    def create_reminder(
        self, title: str, description: str, reminder_type: str, scheduled_time: str
    ):
        """Create a custom reminder"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        valid_types = [t.value for t in ReminderType]
        if reminder_type not in valid_types:
            print(f"✗ Invalid reminder type. Valid options: {', '.join(valid_types)}")
            return

        result = self.app.create_reminder(title, description, reminder_type, scheduled_time)
        if result["success"]:
            print(f"✓ Reminder created: {title}")
            print(f"  ID: {result['reminder_id']}")
            print(f"  Scheduled: {scheduled_time}")
        else:
            print(f"✗ Failed to create reminder: {result['message']}")
        return result

    def setup_daily_expense_reminder(self, hour: int = 20, minute: int = 0):
        """Setup daily expense tracking reminder"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        result = self.app.setup_daily_expense_reminder(hour, minute)
        if result["success"]:
            print(f"✓ Daily expense reminder set for {hour:02d}:{minute:02d}")
        else:
            print(f"✗ Failed to setup reminder: {result['message']}")
        return result

    def setup_daily_checkin_reminder(self, hour: int = 9, minute: int = 0):
        """Setup daily check-in reminder"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        result = self.app.setup_daily_check_in_reminder(hour, minute)
        if result["success"]:
            print(f"✓ Daily check-in reminder set for {hour:02d}:{minute:02d}")
        else:
            print(f"✗ Failed to setup reminder: {result['message']}")
        return result

    def setup_weekly_summary_reminder(self, day_of_week: int = 0, hour: int = 18):
        """Setup weekly summary reminder"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        result = self.app.setup_weekly_summary_reminder(day_of_week, hour)
        if result["success"]:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            print(f"✓ Weekly summary reminder set for {days[day_of_week]} at {hour:02d}:00")
        else:
            print(f"✗ Failed to setup reminder: {result['message']}")
        return result

    def list_reminders(self):
        """List all active reminders"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        reminders = self.app.get_reminders()
        if not reminders:
            print("No active reminders")
            return

        print("\n" + "=" * 70)
        print("ACTIVE REMINDERS")
        print("=" * 70)
        for idx, reminder in enumerate(reminders, 1):
            print(f"{idx}. {reminder[2]} ({reminder[4]})")
            print(f"   {reminder[3]}")
            print(f"   Scheduled: {reminder[5]}")
        print("=" * 70 + "\n")

    def delete_reminder(self, reminder_id: str):
        """Delete a reminder"""
        if not self.app.current_user_id:
            print("✗ Not logged in")
            return

        result = self.app.delete_reminder(reminder_id)
        if result["success"]:
            print(f"✓ Reminder deleted")
        else:
            print(f"✗ Failed to delete reminder: {result['message']}")
        return result

    def help(self):
        """Display help information"""
        help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   WhatsApp Ecosystem CLI - Help                            ║
╚════════════════════════════════════════════════════════════════════════════╝

USER COMMANDS:
  register <username> <phone> <email> <password>
      Register a new user

  login <username> <password>
      Login to your account

  logout
      Logout from current account

  profile
      View your profile information


CONTACT COMMANDS:
  add-contact <name> <phone> [email]
      Add a new contact

  list-contacts
      List all your contacts


EXPENSE COMMANDS:
  log-expense <amount> <category> [description] [payment_method]
      Log an expense
      Categories: food, transport, entertainment, shopping, utilities, healthcare, education, other

  daily-expenses [date]
      View expenses for a specific date (YYYY-MM-DD format, defaults to today)

  weekly-summary
      View weekly expense summary

  monthly-summary [month] [year]
      View monthly expense summary


REMINDER COMMANDS:
  create-reminder <title> <description> <type> <scheduled_time>
      Create a custom reminder
      Types: daily, weekly, monthly, custom
      Scheduled time format: YYYY-MM-DD HH:MM:SS

  setup-daily-expense <hour> [minute]
      Setup daily expense tracking reminder (default 20:00)

  setup-daily-checkin <hour> [minute]
      Setup daily check-in reminder (default 09:00)

  setup-weekly-summary <day> [hour]
      Setup weekly summary reminder
      Days: 0=Monday, 1=Tuesday, ..., 6=Sunday

  list-reminders
      List all active reminders

  delete-reminder <reminder_id>
      Delete a reminder


OTHER COMMANDS:
  help
      Show this help message

  exit
      Exit the CLI
        """
        print(help_text)

    def close(self):
        """Close the CLI and cleanup"""
        self.app.close()
        print("\n✓ WhatsApp Ecosystem closed. Goodbye!")

    def run_interactive(self):
        """Run interactive CLI session"""
        print("\n" + "=" * 70)
        print("WhatsApp Ecosystem CLI")
        print("=" * 70)
        print("Type 'help' for commands or 'exit' to quit\n")

        while True:
            try:
                user_input = input(">>> ").strip()
                if not user_input:
                    continue

                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]

                if command == "exit":
                    self.close()
                    break
                elif command == "help":
                    self.help()
                elif command == "register" and len(args) >= 4:
                    self.register(args[0], args[1], args[2], args[3])
                elif command == "login" and len(args) >= 2:
                    self.login(args[0], args[1])
                elif command == "logout":
                    self.logout()
                elif command == "profile":
                    self.profile()
                elif command == "add-contact" and len(args) >= 2:
                    email = args[3] if len(args) > 3 else None
                    self.add_contact(args[0], args[1], email)
                elif command == "list-contacts":
                    self.list_contacts()
                elif command == "log-expense" and len(args) >= 2:
                    amount = float(args[0])
                    category = args[1]
                    description = args[2] if len(args) > 2 else None
                    payment_method = args[3] if len(args) > 3 else None
                    self.log_expense(amount, category, description, payment_method)
                elif command == "daily-expenses":
                    date = args[0] if args else None
                    self.view_daily_expenses(date)
                elif command == "weekly-summary":
                    self.view_weekly_summary()
                elif command == "monthly-summary":
                    month = int(args[0]) if len(args) > 0 else None
                    year = int(args[1]) if len(args) > 1 else None
                    self.view_monthly_summary(month, year)
                elif command == "create-reminder" and len(args) >= 4:
                    self.create_reminder(args[0], args[1], args[2], args[3])
                elif command == "setup-daily-expense":
                    hour = int(args[0]) if args else 20
                    minute = int(args[1]) if len(args) > 1 else 0
                    self.setup_daily_expense_reminder(hour, minute)
                elif command == "setup-daily-checkin":
                    hour = int(args[0]) if args else 9
                    minute = int(args[1]) if len(args) > 1 else 0
                    self.setup_daily_checkin_reminder(hour, minute)
                elif command == "setup-weekly-summary":
                    day = int(args[0]) if args else 0
                    hour = int(args[1]) if len(args) > 1 else 18
                    self.setup_weekly_summary_reminder(day, hour)
                elif command == "list-reminders":
                    self.list_reminders()
                elif command == "delete-reminder" and len(args) >= 1:
                    self.delete_reminder(args[0])
                else:
                    print(
                        f"✗ Unknown command or invalid arguments: {command}. Type 'help' for available commands."
                    )

            except ValueError as e:
                print(f"✗ Invalid input: {e}")
            except KeyboardInterrupt:
                print("\n")
                self.close()
                break
            except Exception as e:
                print(f"✗ Error: {e}")


def main():
    """Main entry point for CLI"""
    cli = WhatsAppCLI()
    cli.run_interactive()


if __name__ == "__main__":
    main()
