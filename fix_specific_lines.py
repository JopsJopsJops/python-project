import os

def fix_specific_lines():
    """Fix the specific line length issues reported by flake8"""

    # Dictionary of file -> line_number -> fix_function
    fixes = {
        'expense_tracker_app/budget_manager.py': {
            42: fix_long_assignment,
            55: fix_long_assignment,
            56: fix_long_assignment,
            161: fix_long_assignment,
            182: fix_long_method_call,
            190: fix_long_assignment,
            198: fix_long_method_call
        },
        'expense_tracker_app/data_manager.py': {
            193: fix_long_assignment,
            199: fix_long_assignment,
            381: fix_long_method_call,
            725: fix_long_assignment
        },
        'expense_tracker_app/dialogs.py': {
            236: fix_long_assignment,
            237: fix_long_assignment,
            239: fix_long_assignment,
            330: fix_long_method_call,
            350: fix_long_assignment,
            373: fix_long_method_call,
            404: fix_long_string,
            405: fix_long_assignment,
            468: fix_long_assignment
        },
        'expense_tracker_app/main.py': {
            457: fix_long_assignment,
            467: fix_long_assignment,
            482: fix_long_assignment,
            483: fix_long_assignment,
            489: fix_long_assignment,
            536: fix_long_method_call,
            790: fix_long_assignment,
            808: fix_long_assignment,
            900: fix_long_string,
            1155: fix_long_assignment
        },
        'expense_tracker_app/widgets.py': {
            771: fix_long_assignment,
            778: fix_long_assignment,
            827: fix_long_assignment,
            1264: fix_long_assignment,
            1290: fix_long_method_call,
            1773: fix_long_assignment,
            2196: fix_long_method_call,
            2201: fix_long_method_call,
            2424: fix_long_assignment,
            2426: fix_long_assignment,
            2448: fix_long_string,
            3682: fix_long_assignment
        },
        'tests/test_budget_data_manager.py': {
            40: fix_long_method_call,
            47: fix_long_assignment,
            57: fix_long_assignment,
            61: fix_long_assignment
        },
        'tests/test_import_service.py': {
            198: fix_long_assignment
        },
        'tests/test_main.py': {
            202: fix_long_assignment
        },
        'tests/test_widgets.py': {
            225: fix_long_method_call,
            490: fix_long_assignment
        }
    }

    for filepath, line_fixes in fixes.items():
        if os.path.exists(filepath):
            print(f"Processing {filepath}...")
            apply_fixes_to_file(filepath, line_fixes)
        else:
            print(f"Warning: {filepath} not found")

def apply_fixes_to_file(filepath, line_fixes):
    """Apply fixes to specific lines in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    for line_num, fix_func in line_fixes.items():
        # Convert to 0-based index
        idx = line_num - 1
        if idx < len(lines):
            original_line = lines[idx]
            fixed_line = fix_func(original_line.rstrip())
            if fixed_line != original_line.rstrip():
                lines[idx] = fixed_line + '\n'
                modified = True
                print(f"  Fixed line {line_num}")

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

def fix_long_assignment(line):
    """Break long assignment statements"""
    if ' = ' in line and len(line) > 88:
        parts = line.split(' = ', 1)
        if len(parts) == 2:
            var_name, value = parts
            # If it's a method call, break after opening parenthesis
            if '(' in value and ')' in value:
                return f"{var_name} = {break_method_call(value)}"
            # Otherwise, break after the equals
            return f"{var_name} = \\\n    {value}"
    return line

def fix_long_method_call(line):
    """Break long method calls"""
    if '(' in line and ')' in line and len(line) > 88:
        return break_method_call(line)
    return line

def fix_long_string(line):
    """Break long strings"""
    if '"""' in line or "'''" in line:
        # Triple-quoted strings - leave alone
        return line

    if len(line) > 88 and ('"' in line or "'" in line):
        # Find string boundaries and break them
        parts = line.split('"')
        if len(parts) >= 3:
            # Simple string breaking - join with concatenation
            pre_string = '"'.join(parts[:-2])
            string_content = parts[-2]
            if len(string_content) > 50:
                # Break the string in half
                mid = len(string_content) // 2
                broken = f'{pre_string}"{string_content[:mid]}" \\\n    "{string_content[mid:]}"'
                return broken
    return line

def break_method_call(line):
    """Break a method call across multiple lines"""
    if '(' in line and ')' in line:
        # Find the opening parenthesis
        paren_idx = line.find('(')
        method_name = line[:paren_idx].strip()
        args = line[paren_idx:]

        # Simple breaking: put each argument on its own line
        if ',' in args:
            args_parts = args.split(',')
            broken_args = ',\n    '.join(args_parts)
            return f"{method_name}(\n    {broken_args}\n)"

    return line

if __name__ == "__main__":
    fix_specific_lines()
    print("Line length fixes applied. Run flake8 again to check remaining issues.")
