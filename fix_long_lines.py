import re
import os

def break_long_lines(filepath, max_length=88):
    """Manually break long lines that Black can't handle"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []

    for line in lines:
        if len(line) > max_length and not line.strip().startswith('#'):
            # Try to break the line
            broken_line = break_line(line, max_length)
            new_lines.extend(broken_line)
        else:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

def break_line(line, max_length):
    """Break a single long line into multiple lines"""
    # Patterns to match for breaking
    patterns = [
        # Method calls with parentheses
        r'(\w+\([^)]+\))',
        # Assignment with long right-hand side
        r'(\w+\s*=\s*.+)',
        # If statements with long conditions
        r'(if\s+.+:)',
        # Return statements
        r'(return\s+.+)',
    ]

    # Try to break at natural points
    break_points = [',', '(', ' and ', ' or ', ' + ', ' - ']

    for break_point in break_points:
        if break_point in line:
            parts = line.split(break_point)
            if len(parts) > 1:
                # Simple breaking logic - you might need to customize this
                potential_lines = []
                current_line = parts[0] + break_point

                for part in parts[1:]:
                    if len(current_line + part) > max_length:
                        potential_lines.append(current_line.rstrip())
                        current_line = '    ' + part  # Indent continuation
                    else:
                        current_line += part + break_point

                if current_line:
                    potential_lines.append(current_line.rstrip(break_point))

                # If we successfully broke the line, return the parts
                if len(potential_lines) > 1 and all(len(l) <= max_length for l in potential_lines):
                    return potential_lines

    # If no good break point found, return the original line
    return [line]

def fix_specific_files():
    """Fix the specific files with line length issues"""
    problem_files = [
        'expense_tracker_app/budget_manager.py',
        'expense_tracker_app/data_manager.py',
        'expense_tracker_app/dialogs.py',
        'expense_tracker_app/main.py',
        'expense_tracker_app/widgets.py',
        'tests/test_budget_data_manager.py',
        'tests/test_import_service.py',
        'tests/test_main.py',
        'tests/test_widgets.py'
    ]

    for filepath in problem_files:
        if os.path.exists(filepath):
            print(f"Processing {filepath}...")
            break_long_lines(filepath)
        else:
            print(f"Warning: {filepath} not found")

if __name__ == "__main__":
    fix_specific_files()
    print("Line breaking completed. Some manual fixes may still be needed.")
