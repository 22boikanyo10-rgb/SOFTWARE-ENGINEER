#!/usr/bin/env python
"""
WhatsApp Ecosystem SaaS - Quick Setup Script
Run this to set up and test the project
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*70}")
    print(f"► {description}")
    print(f"{'='*70}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"✗ Failed: {description}")
        return False
    print(f"✓ Success: {description}")
    return True

def main():
    print("\n" + "="*70)
    print("WhatsApp Ecosystem SaaS - Setup & Test")
    print("="*70)
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("✗ Python 3.10+ required")
        sys.exit(1)
    
    # Setup virtual environment
    if not os.path.exists(".venv"):
        if not run_command("python -m venv .venv", "Create virtual environment"):
            sys.exit(1)
    
    # Activate venv and install dependencies
    if sys.platform == "win32":
        activate_cmd = ".venv\\Scripts\\activate.bat &&"
    else:
        activate_cmd = "source .venv/bin/activate &&"
    
    if not run_command(f"{activate_cmd} pip install --upgrade pip", "Upgrade pip"):
        sys.exit(1)
    
    if not run_command(f"{activate_cmd} pip install -r requirements-dev.txt", "Install dependencies"):
        sys.exit(1)
    
    # Run tests
    if not run_command(f"{activate_cmd} pytest tests/ -v", "Run test suite"):
        print("\n⚠ Some tests failed, but continuing...")
    
    # Run linting
    if not run_command(f"{activate_cmd} ruff check .", "Run linter (ruff)"):
        print("\n⚠ Linting issues found, but continuing...")
    
    # Display success message
    print("\n" + "="*70)
    print("✓ Setup Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Activate your virtual environment:")
    if sys.platform == "win32":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("\n2. Run the CLI:")
    print("   python -m software_engineer")
    print("\n3. Or run tests anytime:")
    print("   pytest tests/ -v")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
