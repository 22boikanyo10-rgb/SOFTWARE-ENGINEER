import sys
import shlex
from whatsapp_ecosystem import WhatsAppEcosystem


def print_help():
    print("Commands:")
    print("  register <username> <phone> <email> <password>")
    print("  login <username> <password>")
    print("  logout")
    print("  profile")
    print("  log-expense <amount> <category> <description>")
    print("  weekly-summary")
    print("  exit")


def main():
    app = WhatsAppEcosystem()
    print("Welcome to SOFTWARE-ENGINEER CLI (minimal)")
    print_help()

    try:
        while True:
            try:
                raw = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw:
                continue
            parts = shlex.split(raw)
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "help":
                print_help()

            elif cmd == "register":
                if len(args) != 4:
                    print("Usage: register <username> <phone> <email> <password>")
                    continue
                username, phone, email, password = args
                user_id = app.register(username, phone, email, password)
                if user_id:
                    print(f"Registered {username} (id={user_id})")
                else:
                    print("Registration failed (username or phone may already exist)")

            elif cmd == "login":
                if len(args) != 2:
                    print("Usage: login <username> <password>")
                    continue
                username, password = args
                ok = app.login(username, password)
                print("Login successful" if ok else "Login failed")

            elif cmd == "logout":
                app.logout()
                print("Logged out")

            elif cmd == "profile":
                profile = app.current_profile()
                if profile:
                    print(profile)
                else:
                    print("No user logged in")

            elif cmd == "log-expense":
                if len(args) < 3:
                    print("Usage: log-expense <amount> <category> <description>")
                    continue
                try:
                    amount = float(args[0])
                except ValueError:
                    print("Amount must be a number")
                    continue
                category = args[1]
                description = " ".join(args[2:])
                eid = app.log_expense(amount, category, description)
                print(f"Logged expense id={eid}")

            elif cmd == "weekly-summary":
                summary = app.get_weekly_summary()
                print("Weekly summary:")
                for row in summary:
                    print(f"  {row['category']}: {row['total']}")

            elif cmd in ("exit", "quit"):
                break

            else:
                print("Unknown command. Type 'help' to see commands.")
    finally:
        app.close()

if __name__ == "__main__":
    main()
