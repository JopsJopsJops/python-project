import os

def safe_fix_long_lines():
    """Safely fix long lines without breaking syntax"""

    fixes = {
        'expense_tracker_app/data_manager.py': {
            193: fix_simple_assignment,
            199: fix_simple_assignment,
            381: fix_simple_assignment,
            725: fix_simple_assignment
        },
        'expense_tracker_app/main.py': {
            457: fix_simple_assignment,
            467: fix_simple_assignment,
            482: fix_simple_assignment,
            483: fix_simple_assignment,
            489: fix_simple_assignment,
            536: fix_simple_assignment,
            790: fix_simple_assignment,
            808: fix_simple_assignment,
            900: fix_long_string_safe,
            1155: fix_simple_assignment
        },
        'tests/test_import_service.py': {
            198: fix_simple_assignment
        },
        'tests/test_main.py': {
            202: fix_simple_assignment
        },
        'tests/test_widgets.py': {
            225: fix_simple_assignment,
            490: fix_simple_assignment
        }
    }

    for filepath, line_fixes in fixes.items():
        if os.path.exists(filepath):
            print(f"Processing {filepath}...")
            safe_apply_fixes(filepath, line_fixes)

def safe_apply_fixes(filepath, line_fixes):
    """Safely apply fixes without breaking syntax"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    for line_num, fix_func in line_fixes.items():
        idx = line_num - 1
        if idx < len(lines):
            original_line = lines[idx].rstrip()
            if len(original_line) > 88:  # Only fix if actually too long
                fixed_line = fix_func(original_line)
                if fixed_line != original_line:
                    lines[idx] = fixed_line + '\n'
                    modified = True
                    print(f"  Fixed line {line_num}")

    if modified:
        # Test if the file still has valid syntax
        if is_valid_python_syntax('\n'.join(lines)):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"  Successfully updated {filepath}")
        else:
            print(f"  WARNING: Fix would break syntax in {filepath}, skipping")

def is_valid_python_syntax(code):
    """Check if Python code has valid syntax"""
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False

def fix_simple_assignment(line):
    """Simple assignment breaking - most conservative approach"""
    if ' = ' in line and len(line) > 88:
        parts = line.split(' = ', 1)
        if len(parts) == 2:
            var_name, value = parts
            # Only break if it's a simple value (not a complex expression)
            if not any(char in value for char in '()[]{}'):
                return f"{var_name} = \\\n    {value}"

    return line

def fix_long_string_safe(line):
    """Safely break long strings"""
    if len(line) > 88 and '"' in line:
        # Count quotes to ensure we have pairs
        if line.count('"') % 2 == 0:  # Even number of quotes
            parts = line.split('"')
            if len(parts) >= 3:
                pre_string = '"'.join(parts[:-2]) + '"'
                string_content = parts[-2]
                if len(string_content) > 30:
                    # Break into two roughly equal parts
                    mid = len(string_content) // 2
                    # Find a space near the middle to break at
                    space_pos = string_content.rfind(' ', 0, mid)
                    if space_pos == -1:
                        space_pos = string_content.find(' ', mid)
                    if space_pos != -1:
                        part1 = string_content[:space_pos]
                        part2 = string_content[space_pos+1:]
                        return f'{pre_string}{part1}" \\\n    "{part2}"'
    return line

if __name__ == "__main__":
    safe_fix_long_lines()
    print("Safe fixes applied. Run flake8 again to check remaining issues.")
