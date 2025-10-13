import ast
import os

def remove_unused_imports(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        
        # Find all imports
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.add(f"{node.module}.{alias.name}")
        
        # Simple heuristic: if import is only used in type hints, keep it
        # For now, we'll just manually fix the obvious ones
        
    except SyntaxError:
        print(f"Syntax error in {filepath}, skipping")
        return

# Manual fixes for the worst offenders
files_to_fix = {
    "expense_tracker_app/dialogs.py": [
        "Remove unused import: 'expense_tracker_app.data_manager.DataManager'"
    ],
    "expense_tracker_app/import_service.py": [
        "Remove unused imports: 'openpyxl', 'csv', 'os' at top",
        "Remove duplicate imports inside functions",
        "Remove unused variable 'success'"
    ],
    "expense_tracker_app/main.py": [
        "Remove unused imports: 'pandas as pd', 'openpyxl', 'csv', 'os', 'fpdf.FPDF'",
        "Remove unused dialog imports"
    ],
    "tests/test_data_manager.py": [
        "Remove unused imports: 'datetime.datetime', 'unittest.mock.Mock', 'unittest.mock.MagicMock'"
    ]
}

print("Please manually fix these files:")
for file, issues in files_to_fix.items():
    print(f"\n{file}:")
    for issue in issues:
        print(f"  - {issue}")
