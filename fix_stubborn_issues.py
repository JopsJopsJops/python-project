import os
import re

def fix_remaining_issues():
    """Fix all remaining flake8 issues that Black couldn't handle"""

    print("Fixing remaining line length issues...")

    # Fix specific files with known issues
    files_to_fix = [
        'expense_tracker_app/budget_manager.py',
        'expense_tracker_app/data_manager.py',
        'expense_tracker_app/dialogs.py',
        'expense_tracker_app/main.py',
        'expense_tracker_app/widgets.py',
        'tests/test_budget_data_manager.py',
        'tests/test_main.py'
    ]

    for filepath in files_to_fix:
        if os.path.exists(filepath):
            print(f"Processing {filepath}...")
            fix_file_line_lengths(filepath)

    print("Fixing f-string issues...")
    fix_fstring_issues()

    print("Verifying no trailing whitespace...")
    remove_all_trailing_whitespace()

def fix_file_line_lengths(filepath):
    """Fix line length issues in a specific file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1
        line_content = line.rstrip()

        # Skip if line is already short enough
        if len(line_content) <= 88:
            new_lines.append(line)
            continue

        # Try to fix long lines
        fixed_line = fix_long_line(line_content)
        if fixed_line != line_content:
            new_lines.append(fixed_line + '\n')
        else:
            # If we can't fix it, keep original
            new_lines.append(line)

    # Write back if changes were made
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def fix_long_line(line):
    """Fix a single long line using multiple strategies"""

    # Strategy 1: Break method calls
    if '(' in line and ')' in line and not line.strip().startswith('#'):
        fixed = break_method_call(line)
        if fixed != line:
            return fixed

    # Strategy 2: Break assignments
    if ' = ' in line and not line.strip().startswith('class '):
        fixed = break_assignment(line)
        if fixed != line:
            return fixed

    # Strategy 3: Break long strings
    if '"' in line or "'" in line:
        fixed = break_long_string(line)
        if fixed != line:
            return fixed

    # Strategy 4: Break with backslash (last resort)
    if len(line) > 88:
        # Try to break at a logical point
        for break_point in [', ', ' and ', ' or ', ' + ', ' - ']:
            if break_point in line:
                idx = line.rfind(break_point, 0, 80)
                if idx != -1:
                    part1 = line[:idx + len(break_point.rstrip())]
                    part2 = line[idx + len(break_point):]
                    return part1 + ' \\\n    ' + part2

    return line

def break_method_call(line):
    """Break long method calls across multiple lines"""
    # Match method calls: something.method(args) or function(args)
    pattern = r'(\s*\w+\.\w+\(|^\s*\w+\()([^)]+)(\))'
    match = re.search(pattern, line)

    if match:
        prefix, args, suffix = match.groups()
        if ',' in args and len(line) > 88:
            arg_list = [arg.strip() for arg in args.split(',')]
            indent = ' ' * (len(line) - len(line.lstrip()))

            new_lines = [prefix]
            for i, arg in enumerate(arg_list):
                if i == len(arg_list) - 1:
                    new_lines.append(f'{indent}    {arg}')
                else:
                    new_lines.append(f'{indent}    {arg},')
            new_lines.append(f'{indent}{suffix}')

            return '\n'.join(new_lines)

    return line

def break_assignment(line):
    """Break long assignment statements"""
    if ' = ' in line and len(line) > 88:
        parts = line.split(' = ', 1)
        var_name, value = parts

        # Don't break if it's a type hint or simple assignment
        if ':' in var_name or len(value) < 30:
            return line

        # Break after equals with backslash
        return f"{var_name} = \\\n    {value}"

    return line

def break_long_string(line):
    """Break long strings"""
    # Match string assignments: var = "long string"
    string_pattern = r'^(\s*\w+\s*=\s*)(["\'])([^"\']+)(["\'])$'
    match = re.match(string_pattern, line)

    if match and len(line) > 88:
        prefix, quote1, content, quote2 = match.groups()

        if len(content) > 50:
            # Find a space near the middle to break at
            mid = len(content) // 2
            space_pos = content.rfind(' ', 0, mid)
            if space_pos == -1:
                space_pos = content.find(' ', mid)

            if space_pos != -1:
                part1 = content[:space_pos]
                part2 = content[space_pos + 1:]
                return f'{prefix}{quote1}{part1}{quote1} \\\n    {quote1}{part2}{quote2}'

    return line

def fix_fstring_issues():
    """Fix f-strings without placeholders"""
    test_file = 'tests/test_budget_data_manager.py'
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove 'f' prefix from strings without {placeholders}
        content = re.sub(r'f"([^"{]*)"', r'"\1"', content)

        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)

def remove_all_trailing_whitespace():
    """Ensure no trailing whitespace anywhere"""
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                cleaned = [line.rstrip() + '\n' for line in lines]

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(cleaned)

if __name__ == "__main__":
    fix_remaining_issues()
    print("Done! Run flake8 again to check remaining issues.")
