import os

def show_problem_lines():
    """Show the actual content of problematic lines"""
    problem_files = {
        'expense_tracker_app/budget_manager.py': [42, 55, 56, 161, 182, 190, 198],
        'expense_tracker_app/data_manager.py': [193, 199, 381, 725],
        'expense_tracker_app/dialogs.py': [236, 237, 239, 330, 350, 373, 404, 405, 468],
        'expense_tracker_app/main.py': [457, 467, 482, 483, 489, 536, 790, 808, 900, 1155],
        'expense_tracker_app/widgets.py': [771, 778, 827, 1264, 1290, 1773, 2196, 2201, 2424, 2426, 2448, 3682],
        'tests/test_budget_data_manager.py': [40, 47, 57, 61],
        'tests/test_import_service.py': [198],
        'tests/test_main.py': [202],
        'tests/test_widgets.py': [225, 490]
    }

    for filepath, line_nums in problem_files.items():
        if os.path.exists(filepath):
            print(f"\n{filepath}:")
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num in line_nums:
                if line_num - 1 < len(lines):
                    line = lines[line_num - 1].rstrip()
                    print(f"  Line {line_num} ({len(line)} chars): {line}")

if __name__ == "__main__":
    show_problem_lines()
