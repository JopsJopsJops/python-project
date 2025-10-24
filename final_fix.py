import os
import re


def fix_all_remaining_issues():
    """Fix all remaining flake8 issues safely"""

    # Fix trailing whitespace in widgets.py (if any remain)
    fix_trailing_whitespace()

    # Fix specific files with manual patterns
    manual_fixes = {
        "expense_tracker_app/budget_manager.py": fix_budget_manager,
        "expense_tracker_app/data_manager.py": fix_data_manager,
        "expense_tracker_app/dialogs.py": fix_dialogs,
        "expense_tracker_app/main.py": fix_main,
        "expense_tracker_app/widgets.py": fix_widgets,
        "tests/test_budget_data_manager.py": fix_test_budget,
        "tests/test_import_service.py": fix_simple_assignment,
        "tests/test_main.py": fix_simple_assignment,
        "tests/test_widgets.py": fix_simple_assignment,
    }

    for filepath, fix_func in manual_fixes.items():
        if os.path.exists(filepath):
            print(f"Processing {filepath}...")
            fix_func(filepath)


def fix_trailing_whitespace():
    """Ensure all trailing whitespace is removed"""
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                cleaned = [line.rstrip() + "\n" for line in lines]

                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(cleaned)


def fix_budget_manager(filepath):
    """Fix budget_manager.py specific issues"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Common fixes for long lines
    content = break_long_assignments(content)
    content = break_long_method_calls(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def fix_data_manager(filepath):
    """Fix data_manager.py specific issues"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = break_long_assignments(content)
    content = break_long_strings(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def fix_dialogs(filepath):
    """Fix dialogs.py specific issues"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = break_long_strings(content)
    content = break_long_assignments(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def fix_main(filepath):
    """Fix main.py specific issues"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = break_long_assignments(content)
    content = break_long_strings(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def fix_widgets(filepath):
    """Fix widgets.py specific issues"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    content = break_long_assignments(content)
    content = break_long_method_calls(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def fix_test_budget(filepath):
    """Fix test_budget_data_manager.py"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove f from strings without placeholders
    content = re.sub(r'f"([^"{]*)"', r'"\1"', content)
    content = break_long_method_calls(content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def fix_simple_assignment(filepath):
    """Simple assignment breaking for test files"""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if len(line) > 88 and " = " in line:
            parts = line.split(" = ", 1)
            if len(parts) == 2:
                new_line = parts[0] + " = \\\n    " + parts[1]
                new_lines.append(new_line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def break_long_assignments(content):
    """Break long assignment statements"""
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        if len(line) > 88 and " = " in line:
            # Try to break after equals
            parts = line.split(" = ", 1)
            if len(parts) == 2:
                var, value = parts
                # If value is a method call, break differently
                if "(" in value and ")" in value:
                    new_line = break_method_call(line)
                    new_lines.append(new_line)
                else:
                    new_lines.append(f"{var} = \\")
                    new_lines.append(f"    {value}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def break_long_method_calls(content):
    """Break long method calls"""
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        if len(line) > 88 and "(" in line and ")" in line:
            # Simple method call breaking
            match = re.match(r"(\s*)(\w+)\s*\((.*)\)", line)
            if match:
                indent, method, args = match.groups()
                if "," in args:
                    arg_lines = [f"{indent}{method}("]
                    for arg in args.split(","):
                        arg_lines.append(f"{indent}    {arg},")
                    arg_lines.append(f"{indent})")
                    new_lines.extend(arg_lines)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def break_long_strings(content):
    """Break long strings"""
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        if len(line) > 88 and '"' in line and line.count('"') >= 2:
            # Find string content
            match = re.search(r'(\s*.*=\s*)"([^"]*)"', line)
            if match:
                prefix, string_content = match.groups()
                if len(string_content) > 50:
                    mid = len(string_content) // 2
                    # Find space near middle
                    space_pos = string_content.rfind(" ", 0, mid)
                    if space_pos == -1:
                        space_pos = string_content.find(" ", mid)
                    if space_pos != -1:
                        part1 = string_content[:space_pos]
                        part2 = string_content[space_pos + 1 :]
                        new_lines.append(f'{prefix}"{part1}" \\')
                        new_lines.append(f'    "{part2}"')
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def break_method_call(line):
    """Break a single method call"""
    # Find the method name and arguments
    match = re.match(r"(\s*)(\w+)\s*\((.*)\)", line)
    if match:
        indent, method, args = match.groups()
        arg_list = [arg.strip() for arg in args.split(",")]

        new_lines = [f"{indent}{method}("]
        for i, arg in enumerate(arg_list):
            if i == len(arg_list) - 1:
                new_lines.append(f"{indent}    {arg}")
            else:
                new_lines.append(f"{indent}    {arg},")
        new_lines.append(f"{indent})")

        return "\n".join(new_lines)
    return line


if __name__ == "__main__":
    fix_all_remaining_issues()
    print("All fixes applied. Run flake8 again to verify.")
