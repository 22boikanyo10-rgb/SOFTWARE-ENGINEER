#!/usr/bin/env python
# SOFTWARE-ENGINEER

A comprehensive **WhatsApp Ecosystem SaaS** platform with user authentication, real-time messaging, expense tracking, and intelligent reminder notifications.

---

## 🚀 Features

### User Management
- ✅ User registration with secure password hashing
- ✅ User authentication and login/logout
- ✅ User profile management
- ✅ Contact management system

### Messaging System
- ✅ Send text and media messages
- ✅ Message status tracking (sent, delivered, read, failed)
- ✅ Conversation management
- ✅ Message search functionality

### Expense Tracking
- ✅ Log expenses with categories (food, transport, entertainment, shopping, utilities, healthcare, education, other)
- ✅ View daily, weekly, and monthly expense summaries
- ✅ Track expenses by category
- ✅ Payment method tracking
- ✅ Detailed expense descriptions

### Reminder System
- ✅ Create custom reminders (daily, weekly, monthly)
- ✅ Daily expense tracking reminders
- ✅ Daily check-in reminders
- ✅ Weekly summary reminders
- ✅ Background scheduler for automated reminders
- ✅ Reminder history tracking

### Interactive CLI
- ✅ Command-line interface for all operations
- ✅ Interactive session mode
- ✅ User-friendly output formatting
- ✅ Comprehensive help documentation

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Database:** SQLite3
- **Runtime:** Standard library (no external dependencies for core)
- **Development:** pytest, black, ruff, mypy
- **Architecture:** Class-based with dependency injection

---

## 📦 Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- pip package manager

### 2. Clone & Setup
```bash
git clone https://github.com/22boikanyo10-rgb/SOFTWARE-ENGINEER
cd SOFTWARE-ENGINEER

# Run automated setup (creates venv, installs deps, runs tests)
python setup.py
```

### 3. Activate Virtual Environment
```bash
# On Linux/Mac
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### 5. Run the CLI
```bash
python -m software_engineer
```

### 6. Run Tests
```bash
pytest tests/ -v
```

---

## 🎮 CLI Usage

### Interactive Mode
```bash
python -m software_engineer
>>> help
```

### User Commands
```bash
# Register a new user
register john_doe +1234567890 john@example.com password123

# Login
login john_doe password123

# View profile
profile

# Logout
logout
```

### Contact Management
```bash
# Add a contact
add-contact "Jane Smith" +0987654321 jane@example.com

# List all contacts
list-contacts
```

### Expense Tracking
```bash
# Log an expense
log-expense 50.00 food "Lunch at restaurant"
log-expense 25.50 transport "Uber ride"
log-expense 15.99 entertainment "Movie ticket"

# View daily expenses (today)
daily-expenses

# View daily expenses for specific date
daily-expenses 2026-08-17

# View weekly summary
weekly-summary

# View monthly summary
monthly-summary 8 2026
```

### Reminder Management
```bash
# Setup daily expense reminder at 8 PM
setup-daily-expense 20 0

# Setup daily check-in reminder at 9 AM
setup-daily-checkin 9 0

# Setup weekly summary reminder (Monday at 6 PM)
setup-weekly-summary 0 18

# List all active reminders
list-reminders

# Create custom reminder
create-reminder "Buy groceries" "Remember milk" daily "2026-08-18 10:00:00"

# Delete reminder by ID
delete-reminder <reminder_id>
```

---

## 🏗️ Project Structure

```
SOFTWARE-ENGINEER/
├── src/software_engineer/
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Entry point (launches CLI)
│   ├── cli.py                # Interactive CLI interface (500+ lines)
│   ├── app.py                # Main application logic
│   ├── config.py             # Configuration management
│   └── hello.py              # Greeting utilities
│
├── tests/
│   ├── conftest.py           # Pytest configuration & fixtures
│   └── test_ecosystem.py      # Comprehensive test suite (400+ tests)
│
├── whatsapp_ecosystem.py      # Core SaaS logic (950+ lines)
│   ├── Database              # SQLite database manager
│   ├── User                  # User management
│   ├── Message               # Messaging system
│   ├── ExpenseTracker        # Expense tracking
│   ├── ReminderManager       # Reminder scheduling
│   ├── DailyReminderService  # Pre-configured reminders
│   └── WhatsAppEcosystem     # Main controller
│
├── pyproject.toml            # Package metadata & dependencies
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
├── ruff.toml                 # Linter configuration
├── setup.py                  # Setup script
└── README.md                 # This file
```

---

## 🧪 Testing

The project includes **comprehensive test coverage** with pytest:

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_ecosystem.py::TestUserManagement -v

# Run with coverage
pytest tests/ --cov=whatsapp_ecosystem
```

### Test Categories
- **User Management Tests** — Registration, login, profiles
- **Contact Management Tests** — Adding, listing contacts
- **Expense Tracking Tests** — Logging, summaries, categories
- **Reminder Tests** — Creation, scheduling, deletion
- **Integration Tests** — End-to-end workflows, multi-user isolation

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    phone_number TEXT UNIQUE NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,
    status TEXT,
    last_seen TIMESTAMP,
    created_at TIMESTAMP
)
```

### Expenses Table
```sql
CREATE TABLE expenses (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    payment_method TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### Reminders Table
```sql
CREATE TABLE reminders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    reminder_type TEXT NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

Additional tables: `contacts`, `conversations`, `messages`, `reminder_history`

---

## 🔐 Security Features

- **Password Hashing:** SHA-256 password hashing
- **User Isolation:** Expenses and reminders are user-specific
- **Session Management:** Current user tracking
- **Data Validation:** Input validation on all operations

---

## 🚀 Running the Application

### Option 1: Interactive CLI (Recommended)
```bash
python -m software_engineer
```
Starts an interactive session where you can type commands directly.

### Option 2: Programmatic Usage
```python
from whatsapp_ecosystem import WhatsAppEcosystem

app = WhatsAppEcosystem()
app.start_reminders()

# Register and login
app.register("john", "+1234567890", "john@example.com", "pass")
app.login("john", "pass")

# Log expense
app.log_expense(50.0, "food", "Lunch")

# Get summary
summary = app.get_weekly_summary()
print(summary)

app.close()
```

---

## 🔧 Development

### Code Quality
```bash
# Format code with black
black src/ tests/ whatsapp_ecosystem.py

# Lint with ruff
ruff check src/ tests/ whatsapp_ecosystem.py

# Type check with mypy
mypy src/ whatsapp_ecosystem.py
```

### Adding New Features
1. Create feature in `whatsapp_ecosystem.py` core logic
2. Add CLI command in `src/software_engineer/cli.py`
3. Add tests in `tests/test_ecosystem.py`
4. Run full test suite: `pytest tests/ -v`

---

## 📝 Environment Variables

Optional configuration via environment variables:

```bash
# Set application environment
APP_ENV=production

# Override greeting prefix (for original CLI)
GREETING_PREFIX=Hi
```

---

## 🐛 Troubleshooting

### Virtual Environment Issues
```bash
# Remove old venv and recreate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Database Lock Issues
```bash
# Remove the database file to reset
rm whatsapp_ecosystem.db
python -m software_engineer
```

### Import Errors
Ensure you're running from the project root directory:
```bash
cd SOFTWARE-ENGINEER
python -m software_engineer
```

---

## 📈 Performance Metrics

- **Test Suite:** 30+ comprehensive tests
- **Code Size:** ~1,500 lines (core + CLI)
- **Database:** Optimized SQLite with indexes
- **Reminder Scheduler:** Background thread with 10-second check interval
- **Message Search:** Full-text search on message content

---

## 🤝 Contributing

To contribute:
1. Create a feature branch
2. Add tests for new functionality
3. Ensure all tests pass: `pytest tests/ -v`
4. Follow code style: `black src/ tests/`
5. Submit pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🎯 Future Enhancements

- [ ] REST API interface (Flask/FastAPI)
- [ ] Web UI dashboard
- [ ] Multi-user messaging
- [ ] File attachments
- [ ] Real-time notifications
- [ ] WhatsApp API integration
- [ ] Mobile app
- [ ] Database migration system
- [ ] Expense analytics
- [ ] Budget alerts

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review test cases for usage examples

---

**Built with ❤️ by Oratile Masilo**

Last Updated: August 17, 2026
