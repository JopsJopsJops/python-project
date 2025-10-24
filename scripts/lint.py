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
    print("🔍 Running code quality checks...")
    result = subprocess.run(["ruff", "check", "expense_tracker_app/", "tests/"])
    sys.exit(result.returncode)

    all_passed = True

    # Check formatting
    print("📝 Checking code formatting...")
    if not run_command("black --check expense_tracker_app/ tests/"):
        print("❌ Code formatting issues found")
        all_passed = False

    # Check imports
    print("📦 Checking import sorting...")
    if not run_command("isort --check-only expense_tracker_app/ tests/"):
        print("❌ Import sorting issues found")
        all_passed = False

    # Check linting
    print("✨ Running flake8...")
    if not run_command("flake8 expense_tracker_app/ tests/ --max-line-length=100"):
        print("❌ Flake8 issues found")
        all_passed = False

    if all_passed:
        print("✅ All code quality checks passed!")
    else:
        print("❌ Code quality checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
