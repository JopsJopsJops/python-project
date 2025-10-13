import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class DataManager:
    def __init__(self, filename="expenses.json", file_path=None):
        # Allow file_path parameter for tests
        if file_path:
            self.filename = file_path
        else:
            self.filename = filename
        self.expenses = {}
        self.categories = [
            "Food",
            "Medical",
            "Utilities",
            "Travel",
            "Clothing",
            "Transportation",
            "Vehicle",
            "Uncategorized",
        ]
        self.last_deleted = None
        self.last_cleared = None  # Add this for clear undo
        self.load_expense()

    def load_expense(self, file_path=None):
        """Load expenses from file. Accepts optional file_path for testing."""
        filename_to_load = file_path if file_path else self.filename

        if not os.path.exists(filename_to_load):
            logger.info(
                "No existing expense file found, starting fresh: %s", filename_to_load
            )
            return

        try:
            with open(filename_to_load, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.expenses = data.get("expenses", {})
                self.categories = data.get("categories", self.categories)

                # Ensure all expenses have IDs
                expense_id = 1
                for category, records in self.expenses.items():
                    for record in records:
                        if "id" not in record:
                            record["id"] = expense_id
                            expense_id += 1

                logger.info(
                    "Loaded %d categories and %d total expenses from %s",
                    len(self.categories),
                    sum(len(v) for v in self.expenses.values()),
                    filename_to_load,
                )

        except (json.JSONDecodeError, FileNotFoundError):
            self.expenses = {}
            self.categories = [
                "Food",
                "Medical",
                "Utilities",
                "Travel",
                "Clothing",
                "Transportation",
                "Vehicle",
                "Uncategorized",
            ]
            logger.warning(
                "Failed to load expenses from %s, starting fresh", filename_to_load
            )
        except Exception as e:
            logger.error("Failed to load expenses: %s", e)
            self.expenses = {}

    def save_data(self, file_path=None):
        """Save data to file. Accepts optional file_path for testing."""
        filename_to_save = file_path if file_path else self.filename

        # Handle empty filename case (tests with no file)
        if not filename_to_save:
            logger.debug("No filename specified for save, skipping")
            return

        data = {"expenses": self.expenses, "categories": self.categories}
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(filename_to_save)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(filename_to_save, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info("Saved data to %s", filename_to_save)
        except Exception as e:
            logger.error("Failed to save data: %s", e)

    def add_category(self, category, merge_target=None):
        """Add category with optional merge functionality."""
        if merge_target:
            # This is a merge operation
            if category not in self.expenses or merge_target not in self.categories:
                raise ValueError("Cannot merge: category or target not found")

            # Move all expenses from category to merge_target
            if category in self.expenses:
                self.expenses.setdefault(merge_target, []).extend(
                    self.expenses[category]
                )
                del self.expenses[category]

            # Remove the old category
            if category in self.categories:
                self.categories.remove(category)
        else:
            # Normal category addition
            if category not in self.categories:
                self.categories.append(category)

        self.save_data()
        logger.info("Added/merged category: %s", category)

    def remove_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
            self.save_data()
            logger.warning("Removed category: %s", category)
        else:
            logger.debug("Attempted to remove non-existent category: %s", category)

    def add_expense(self, category, amount, date, description):
        """Add expense with validation."""

        # Validate amount
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number")

        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

        # If category is not in the list, add it
        if category not in self.categories:
            self.categories.append(category)

        # Generate unique ID for the expense
        all_expenses = self.list_all_expenses()
        max_id = max([e.get("id", 0) for e in all_expenses]) if all_expenses else 0
        new_id = max_id + 1

        new_record = {
            "id": new_id,
            "amount": amount_float,
            "date": date,
            "description": description,
        }
        self.expenses.setdefault(category, []).append(new_record)
        self.save_data()
        logger.info("Added expense in %s: %s", category, new_record)

    def delete_expense(self, category, record):
        """Delete expense - handle both record dict and index."""
        if category not in self.expenses:
            return False

        # Handle index-based deletion (for tests)
        if isinstance(record, int):
            if 0 <= record < len(self.expenses[category]):
                record_to_delete = self.expenses[category][record]
                self.expenses[category].remove(record_to_delete)
                self.last_deleted = (category, record_to_delete)
                self.save_data()
                logger.warning(
                    "Deleted expense from %s: %s", category, record_to_delete
                )
                return True
            else:
                return False

        # Normal record-based deletion - check by value, not reference
        if record in self.expenses[category]:
            self.expenses[category].remove(record)
            self.last_deleted = (category, record)
            self.save_data()
            logger.warning("Deleted expense from %s: %s", category, record)
            return True

        # If we get here, the record wasn't found by value comparison
        # Try to find by content matching for test compatibility
        for existing_record in self.expenses[category]:
            if (
                existing_record.get("amount") == record.get("amount")
                and existing_record.get("date") == record.get("date")
                and existing_record.get("description") == record.get("description")
            ):
                self.expenses[category].remove(existing_record)
                self.last_deleted = (category, existing_record)
                self.save_data()
                logger.warning("Deleted expense from %s: %s", category, existing_record)
                return True

        logger.debug("Delete failed for record: %s", record)
        return False

    def undo_delete(self):
        """Undo last delete or clear operation."""
        # First try to undo a clear
        if self.last_cleared is not None:
            self.expenses = self.last_cleared
            self.last_cleared = None
            self.save_data()
            logger.info("Undo clear: restored all expenses")
            return True

        # Then try to undo a single delete
        if self.last_deleted:
            category, record = self.last_deleted
            self.expenses.setdefault(category, []).append(record)
            self.last_deleted = None
            self.save_data()
            logger.info("Undo delete: restored %s", record)
            return True

        logger.debug("No operation to undo")
        return False

    def undo_last_delete(self):
        """Undo last operation - return None when nothing to undo for tests."""
        result = self.undo_delete()
        return None if not result else result

    def get_sorted_expenses(self):
        """Return expenses dict with records sorted by date (asc)."""
        out = {}
        for cat, records in self.expenses.items():
            try:
                out[cat] = sorted(
                    records,
                    key=lambda r: (
                        datetime.strptime(r.get("date", ""), "%Y-%m-%d")
                        if r.get("date")
                        else datetime.max
                    ),
                )
            except Exception:
                out[cat] = list(records)
        return out

    def get_category_subtotals(self):
        return {
            category: sum(rec.get("amount", 0.0) for rec in records)
            for category, records in self.expenses.items()
        }

    def search_expenses(self, keyword):
        """
        Search expenses by keyword in description.
        Returns a list of (category, record) tuples.
        """
        results = []
        for category, records in self.expenses.items():
            for record in records:
                if keyword.lower() in record.get("description", "").lower():
                    results.append((category, record))
        logger.debug(
            "Search for keyword='%s' returned %d results", keyword, len(results)
        )
        return results

    def get_all_categories(self):
        return list(self.expenses.keys())

    def update_expense(self, old_category, old_record, new_data):
        """
        Update an existing expense. Removes the old record from its category
        and inserts the updated one (possibly in a new category).
        Falls back to old_record values if new_data is incomplete.
        """
        if (
            old_category not in self.expenses
            or old_record not in self.expenses[old_category]
        ):
            return False  # ✅ return False if nothing found

        self.expenses[old_category].remove(old_record)

        category = new_data.get("category", old_category)
        amount = float(new_data.get("amount", old_record.get("amount", 0)))
        date = new_data.get("date", old_record.get("date", ""))
        desc = new_data.get("description", old_record.get("description", ""))

        self.expenses.setdefault(category, []).append(
            {"amount": amount, "date": date, "description": desc}
        )
        self.save_data()
        logger.info("Updated expense from %s → %s", old_record, new_data)
        return True

    def get_expenses_for_category(self, category):
        """Return all expenses for a given category."""
        return self.expenses.get(category, [])

    def get_category_subtotals(self):
        """Return a dict of {category: subtotal_amount}."""
        subtotals = {
            category: sum(rec.get("amount", 0.0) or 0.0 for rec in records)
            for category, records in self.expenses.items()
        }
        logger.debug("Calculated category subtotals: %s", subtotals)
        return subtotals

    def get_grand_total(self):
        """Return the sum of all expenses."""
        grand_total = sum(
            rec.get("amount", 0.0) or 0.0
            for records in self.expenses.values()
            for rec in records
        )
        logger.debug("Calculated grand total: %.2f", grand_total)
        return grand_total

    def get_monthly_totals(self):
        """
        Return a dict of {YYYY-MM: total_amount} for all expenses.
        Useful for trends and time-series analysis.
        """
        monthly_totals = {}
        for records in self.expenses.values():
            for rec in records:
                date = rec.get("date", "")
                amount = rec.get("amount", 0.0) or 0.0
                if date:
                    month = date[:7]  # YYYY-MM
                    monthly_totals[month] = monthly_totals.get(month, 0.0) + amount

        logger.debug("Calculated monthly totals: %s", monthly_totals)
        return monthly_totals

    # ---------- Testable helpers ----------

    def list_all_expenses(self):
        """
        Return a flat list of all expenses as dicts.
        Useful for testing, debugging, and exports.
        """
        all_expenses = []
        for category, records in self.expenses.items():
            for rec in records:
                all_expenses.append(
                    {
                        "category": category,
                        "amount": rec.get("amount", 0.0),
                        "date": rec.get("date", ""),
                        "description": rec.get("description", ""),
                    }
                )
        return all_expenses

    def has_expenses(self):
        """Quick check if any expenses exist."""
        return bool(self.expenses)

    def clear_all(self):
        """Clear all expenses but save for undo."""
        self.last_cleared = self.expenses.copy()
        self.expenses = {}
        self.save_data()
        logger.warning("All expenses cleared")

    def undo_clear(self):
        """Restore expenses after clear_all."""
        if hasattr(self, "last_cleared") and self.last_cleared:
            self.expenses = self.last_cleared
            self.last_cleared = None
            self.save_data()
            logger.info("Undo clear: restored all expenses")
            return True
        return False

    def list_expenses(self):
        """Return expenses by category (alias for get_sorted_expenses for test compatibility)."""
        return self.get_sorted_expenses()

    def get_all_expenses(self):
        """Alias for list_all_expenses for test compatibility."""
        return self.list_all_expenses()
