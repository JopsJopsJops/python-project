import json
from datetime import datetime

# Load the expenses.json file
with open('expenses.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

expenses = data.get('expenses', {})
cleaned_expenses = {}

for category, records in expenses.items():
    valid_records = []
    for r in records:
        date_str = r.get('date', '')
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            valid_records.append(r)
        except Exception:
            # skip records with invalid date
            continue
    if valid_records:
        cleaned_expenses[category] = valid_records

# Save cleaned data back to expenses.json (backup old file first)
import shutil
shutil.copy('expenses.json', 'expenses.json.bak')

data['expenses'] = cleaned_expenses
with open('expenses.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print('expenses.json cleaned! Invalid records removed. Backup saved as expenses.json.bak')
