import os


def apply_targeted_fixes():
    """Apply specific fixes for known problem patterns"""

    # Fix data_manager.py import
    data_manager_path = "expense_tracker_app/data_manager.py"
    if os.path.exists(data_manager_path):
        with open(data_manager_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find the problematic import (line 7, but index 6)
        if len(lines) > 6:
            problematic_import = lines[6]
            # Move it to top (after shebang and docstring if any)
            # This is a simplified approach - you might need to customize
            new_lines = lines[:2] + [problematic_import] + lines[2:6] + lines[7:]

            with open(data_manager_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        print("Fixed data_manager.py import order")

    # Fix f-string issues
    fix_fstring_issues()


def fix_fstring_issues():
    """Remove f prefix from strings without placeholders"""

    # main.py line 835
    main_path = "expense_tracker_app/main.py"
    if os.path.exists(main_path):
        with open(main_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) > 834:
            line_835 = lines[834]
            if 'f"' in line_835 and "{" not in line_835:
                lines[834] = line_835.replace('f"', '"')

        with open(main_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Fixed main.py f-string issue")

    # test_budget_data_manager.py lines 37 and 74
    test_path = "tests/test_budget_data_manager.py"
    if os.path.exists(test_path):
        with open(test_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Line 37 (index 36)
        if len(lines) > 36 and 'f"' in lines[36] and "{" not in lines[36]:
            lines[36] = lines[36].replace('f"', '"')

        # Line 74 (index 73)
        if len(lines) > 73 and 'f"' in lines[73] and "{" not in lines[73]:
            lines[73] = lines[73].replace('f"', '"')

        with open(test_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print("Fixed test f-string issues")


if __name__ == "__main__":
    apply_targeted_fixes()
    print("Targeted fixes applied. Run flake8 again to check remaining issues.")
