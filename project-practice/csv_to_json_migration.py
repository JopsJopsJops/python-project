import csv
import json
import os

csv_file = "expenses.csv"
json_file = "expenses.json"

# Default categories if none exist yet
default_categories = ["Food", "Medical", "Utilities", "Travel",
                      "Clothing", "Transportation", "Vehicle"]

expenses = {}

# Step 1: Read CSV
if os.path.exists(csv_file):
    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row["category"]
            expenses.setdefault(category, []).append({
                "amount": float(row["amount"]),
                "date": row["date"],
                "description": row["description"]
            })

# Step 2: Build JSON structure
data = {
    "expenses": expenses,
    "categories": list(expenses.keys()) or default_categories
}

# Step 3: Save to JSON
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"✅ Migration complete! Data saved to {json_file}")
