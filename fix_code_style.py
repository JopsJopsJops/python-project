import os
import subprocess
import sys

def remove_trailing_whitespace():
    """Remove trailing whitespace from all Python files"""
    directories = ["expense_tracker_app", "tests"]

    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    print(f"Processing {filepath}")

                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Remove trailing whitespace from each line
                    cleaned_lines = [line.rstrip() + '\n' for line in lines]

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(cleaned_lines)

def run_black():
    """Run black formatter"""
    try:
        subprocess.run([
            sys.executable, "-m", "black",
            "expense_tracker_app/", "tests/",
            "--line-length", "88"
        ], check=True)
        print("Black formatting completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Black formatting failed: {e}")

if __name__ == "__main__":
    print("Removing trailing whitespace...")
    remove_trailing_whitespace()

    print("Running black formatter...")
    run_black()

    print("Done! Run flake8 again to check remaining issues.")
