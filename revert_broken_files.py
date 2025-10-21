import os
import shutil
from pathlib import Path

def revert_broken_files():
    """Revert files that have syntax errors"""
    broken_files = [
        'expense_tracker_app/budget_manager.py',
        'expense_tracker_app/dialogs.py',
        'expense_tracker_app/widgets.py',
        'tests/test_budget_data_manager.py'
    ]

    # Create backups first (just in case)
    for filepath in broken_files:
        if os.path.exists(filepath):
            backup_path = filepath + '.backup'
            shutil.copy2(filepath, backup_path)
            print(f"Backed up {filepath} to {backup_path}")

    # Now restore from git (if you're using git)
    try:
        import subprocess
        for filepath in broken_files:
            if os.path.exists(filepath):
                result = subprocess.run(['git', 'checkout', '--', filepath],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Reverted {filepath}")
                else:
                    print(f"Could not revert {filepath} via git")
    except:
        print("Git not available, you'll need to manually fix the syntax errors")

if __name__ == "__main__":
    revert_broken_files()
