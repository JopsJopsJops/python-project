#!/usr/bin/env python3
import subprocess
import sys


def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    print("🚀 Running code formatting...")
    subprocess.run(["ruff", "check", "--fix", "expense_tracker_app/", "tests/"])
    subprocess.run(["black", "expense_tracker_app/", "tests/"])

    # Format imports
    print("📦 Sorting imports with isort...")
    if not run_command("isort expense_tracker_app/ tests/"):
        print("❌ isort failed")
        sys.exit(1)

    # Format code
    print("🎨 Formatting code with black...")
    if not run_command("black expense_tracker_app/ tests/"):
        print("❌ black failed")
        sys.exit(1)

    print("✅ Formatting complete!")


if __name__ == "__main__":
    main()
