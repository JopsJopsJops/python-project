import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
from expense_tracker_app.budget_manager import BudgetManager

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
        self.budget_manager = BudgetManager(self)

    def debug_expense_categories(self):
        """Debug method to see what categories actually have expenses."""
        print("=== DEBUG EXPENSE CATEGORIES ===")
        all_expenses = self.list_all_expenses()
        
        # Group expenses by category
        categories_with_expenses = {}
        for expense in all_expenses:
            category = expense.get('category', 'Unknown')
            if category not in categories_with_expenses:
                categories_with_expenses[category] = []
            categories_with_expenses[category].append(expense)
        
        print(f"Total expenses: {len(all_expenses)}")
        print("Categories with expenses:")
        for category, expenses in categories_with_expenses.items():
            total = sum(exp.get('amount', 0) for exp in expenses)
            print(f"  '{category}': {len(expenses)} expenses, Total: ₱{total:.2f}")
        
        print("Budgets set:")
        for category, budget in self.budget_manager.budgets.items():
            print(f"  '{category}': ₱{budget:.2f}")
        
        # Check if budget categories match expense categories
        mismatches = []
        for budget_cat in self.budget_manager.budgets.keys():
            if budget_cat not in categories_with_expenses:
                mismatches.append(f"Budget category '{budget_cat}' has no expenses")
        
        if mismatches:
            print("CATEGORY MISMATCHES:")
            for mismatch in mismatches:
                print(f"  ❌ {mismatch}")
        
        print("=== END DEBUG ===")

    def debug_category_matching(self):
        """Debug method to check category name matching."""
        print("=== DEBUG CATEGORY MATCHING ===")
        
        # Get all unique categories from expenses
        all_expenses = self.list_all_expenses()
        expense_categories = set(exp.get('category') for exp in all_expenses)
        
        print("Categories found in expenses:")
        for cat in sorted(expense_categories):
            print(f"  '{cat}'")
        
        print("Budgets set for categories:")
        for cat in self.budget_manager.budgets.keys():
            print(f"  '{cat}'")
        
        # Check for exact matches
        matches = []
        mismatches = []
        for budget_cat in self.budget_manager.budgets.keys():
            if budget_cat in expense_categories:
                matches.append(budget_cat)
            else:
                mismatches.append(budget_cat)
        
        print("MATCHES:")
        for match in matches:
            print(f"  ✅ '{match}' - budget will work")
        
        print("MISMATCHES:")
        for mismatch in mismatches:
            print(f"  ❌ '{mismatch}' - no expenses found with this exact name")
            # Suggest possible matches
            possible_matches = [ec for ec in expense_categories if ec.lower() == mismatch.lower()]
            if possible_matches:
                print(f"     💡 Possible match: '{possible_matches[0]}'")
        
        print("=== END DEBUG ===")

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
        """Add category with proper capitalization and duplicate checking"""
        if not category or not category.strip():
            return False, "Category cannot be empty"
        
        normalized_category = self.normalize_category_name(category)
        
        # Check if category already exists
        exists, existing_name = self.category_exists(category)
        if exists:
            # If user entered the exact same category (same capitalization), treat as success
            if category == existing_name:
                return True, f"Category '{existing_name}' is already in your list"
            else:
                return False, f"Category '{existing_name}' already exists (you entered '{category}')"
        
        if merge_target:
            # This is a merge operation
            normalized_merge_target = self.normalize_category_name(merge_target)
            if category not in self.expenses or normalized_merge_target not in self.categories:
                raise ValueError("Cannot merge: category or target not found")

            # Move all expenses from category to merge_target
            if category in self.expenses:
                self.expenses.setdefault(normalized_merge_target, []).extend(
                    self.expenses[category]
                )
                del self.expenses[category]

            # Remove the old category
            if category in self.categories:
                self.categories.remove(category)
        else:
            # Normal category addition - ADD THE NORMALIZED VERSION
            if normalized_category not in self.categories:
                self.categories.append(normalized_category)  # ✅ Add normalized version
                self.categories.sort()  # Keep sorted

        self.save_data()
        logger.info("Added/merged category: %s", normalized_category)
        return True, f"Category '{normalized_category}' added successfully"

    def normalize_category_name(self, category):
        """Normalize category name to proper capitalization"""
        if not category or not category.strip():
            return category
        
        # Remove extra spaces and capitalize each word
        normalized = ' '.join(word.strip().capitalize() for word in category.split())
        return normalized

    def category_exists(self, category):
        """Check if category already exists (case-insensitive)"""
        normalized_input = self.normalize_category_name(category)
        
        # Check in existing categories
        for existing_category in self.categories:
            normalized_existing = self.normalize_category_name(existing_category)
            if normalized_existing == normalized_input:
                return True, existing_category  # Return True and the existing category name
        
        return False, None

    def migrate_categories_to_proper_case(self):
        """Migrate all existing categories and expenses to proper capitalization"""
        logger.info("🔄 Migrating categories to proper capitalization...")
        
        # Create a mapping of old category names to new normalized names
        category_mapping = {}
        
        # Normalize main categories list
        new_categories = []
        for category in self.categories:
            normalized = self.normalize_category_name(category)
            if normalized not in new_categories:
                new_categories.append(normalized)
            if category != normalized:
                category_mapping[category] = normalized
        
        self.categories = sorted(new_categories)
        
        # Normalize expense categories and merge duplicates
        new_expenses = {}
        for old_category, expenses_list in self.expenses.items():
            new_category = self.normalize_category_name(old_category)
            
            if new_category in new_expenses:
                # Merge expenses from duplicate category
                new_expenses[new_category].extend(expenses_list)
                logger.info(f"📂 Merged '{old_category}' into '{new_category}'")
            else:
                new_expenses[new_category] = expenses_list
                if old_category != new_category:
                    logger.info(f"🔄 Renamed '{old_category}' to '{new_category}'")
        
        self.expenses = new_expenses
        
        # Normalize budget categories
        if hasattr(self, 'budget_manager') and hasattr(self.budget_manager, 'budgets'):
            new_budgets = {}
            for old_category, budget_amount in self.budget_manager.budgets.items():
                new_category = self.normalize_category_name(old_category)
                if new_category in new_budgets:
                    # Keep the higher budget if there are duplicates
                    new_budgets[new_category] = max(new_budgets[new_category], budget_amount)
                else:
                    new_budgets[new_category] = budget_amount
            
            self.budget_manager.budgets = new_budgets
        
        self.save_data()
        logger.info("✅ Categories migrated to proper capitalization")
        return len(category_mapping)

    def auto_merge_duplicate_categories(self):
        """Automatically find and merge duplicate categories (case-insensitive)"""
        logger.info("🔄 Looking for duplicate categories to merge...")
        
        # Find duplicate categories (case-insensitive)
        category_groups = {}
        for category in list(self.expenses.keys()):
            normalized = self.normalize_category_name(category)
            if normalized not in category_groups:
                category_groups[normalized] = []
            category_groups[normalized].append(category)
        
        # Merge duplicates
        merged_count = 0
        for normalized_category, duplicates in category_groups.items():
            if len(duplicates) > 1:
                logger.info(f"📂 Found duplicates for '{normalized_category}': {duplicates}")
                
                # Merge all duplicates into the normalized version
                all_expenses = []
                for duplicate in duplicates:
                    if duplicate in self.expenses:
                        all_expenses.extend(self.expenses[duplicate])
                        if duplicate != normalized_category:
                            del self.expenses[duplicate]
                            logger.info(f"🗑️ Removed duplicate category: '{duplicate}'")
                
                # Add merged expenses to normalized category
                self.expenses[normalized_category] = all_expenses
                merged_count += 1
        
        # Update categories list
        self.categories = sorted(list(set(self.normalize_category_name(cat) for cat in self.categories)))
        
        if merged_count > 0:
            self.save_data()
            logger.info(f"✅ Merged {merged_count} groups of duplicate categories")
        
        return merged_count

    def remove_category(self, category, merge_to=None):
        """Remove category with option to merge expenses to another category"""
        normalized_category = self.normalize_category_name(category)
        
        if normalized_category not in self.categories:
            return False, "Category not found"
        
        # Always ensure 'Uncategorized' exists if we might need it
        if "Uncategorized" not in self.categories:
            self.categories.append("Uncategorized")
        
        # If category has expenses
        if normalized_category in self.expenses and self.expenses[normalized_category]:
            if merge_to is None:
                # Default to Uncategorized
                merge_to = "Uncategorized"
            else:
                merge_to = self.normalize_category_name(merge_to)
                # Ensure merge target exists in categories
                if merge_to not in self.categories and merge_to != "Uncategorized":
                    self.categories.append(merge_to)
            
            # Move expenses to merge target
            if merge_to in self.expenses:
                self.expenses[merge_to].extend(self.expenses[normalized_category])
            else:
                self.expenses[merge_to] = self.expenses[normalized_category]
            
            logger.info(f"📂 Moved {len(self.expenses[normalized_category])} expenses from '{normalized_category}' to '{merge_to}'")
        
        # Remove the category from expenses if it exists
        if normalized_category in self.expenses:
            del self.expenses[normalized_category]
        
        # Remove from categories list
        if normalized_category in self.categories:
            self.categories.remove(normalized_category)
        
        self.save_data()
        logger.warning("Removed category: %s", normalized_category)
        return True, f"Category '{normalized_category}' removed successfully"

    def add_expense(self, category, amount, date, description):
        """Add expense with validation and normalized category."""

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

        # Normalize category name
        normalized_category = self.normalize_category_name(category)
        
        # If normalized category is not in the list, add it
        if normalized_category not in self.categories:
            self.categories.append(normalized_category)
            self.categories.sort()

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
        self.expenses.setdefault(normalized_category, []).append(new_record)
        self.save_data()
        logger.info("Added expense in %s: %s", normalized_category, new_record)
        
        # NEW: Update budget alerts after adding expense
        self.update_budget_alerts()
        self.debug_expense_categories()
        
        return True
    
    def update_budget_alerts(self):
        """Update budget alerts and refresh dashboard if available."""
        if hasattr(self, 'budget_manager'):
            alerts = self.budget_manager.check_budget_alerts()
            logger.info(f"💰 Budget alerts updated: {len(alerts)} alerts")
            for alert in alerts:
                logger.info(f"   - {alert}")
            
            # NEW: Trigger dashboard refresh
            self.trigger_dashboard_refresh()

    def trigger_dashboard_refresh(self):
        """Trigger dashboard refresh across the application."""
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QTimer
            
            # Use QTimer to safely refresh the UI in the next event loop
            QTimer.singleShot(100, self._refresh_all_dashboards)
            
        except Exception as e:
            logger.error(f"Error triggering dashboard refresh: {e}")    

    def _refresh_all_dashboards(self):
        """Refresh all dashboard widgets."""
        try:
            from PyQt5.QtWidgets import QApplication, QWidget
            
            for w in QApplication.topLevelWidgets():
                for child in w.findChildren(QWidget):
                    if hasattr(child, "update_dashboard"):
                        try:
                            child.update_dashboard()
                        except Exception as e:
                            logger.debug(f"Error updating dashboard widget: {e}")
        except Exception as e:
            logger.error(f"Error in dashboard refresh: {e}")     

    def delete_expense(self, category, record):
        """Delete expense - handle both record dict and index."""
        normalized_category = self.normalize_category_name(category)
        if normalized_category not in self.expenses:
            return False

        # Handle index-based deletion (for tests)
        if isinstance(record, int):
            if 0 <= record < len(self.expenses[normalized_category]):
                record_to_delete = self.expenses[normalized_category][record]
                self.expenses[normalized_category].remove(record_to_delete)
                self.last_deleted = (normalized_category, record_to_delete)
                self.save_data()
                logger.warning(
                    "Deleted expense from %s: %s", normalized_category, record_to_delete
                )
                # NEW: Update budget alerts after deletion
                self.update_budget_alerts()
                return True
            else:
                return False

        # Normal record-based deletion - check by value, not reference
        if record in self.expenses[normalized_category]:
            self.expenses[normalized_category].remove(record)
            self.last_deleted = (normalized_category, record)
            self.save_data()
            logger.warning("Deleted expense from %s: %s", normalized_category, record)
            # NEW: Update budget alerts after deletion
            self.update_budget_alerts()
            return True

        # If we get here, the record wasn't found by value comparison
        # Try to find by content matching for test compatibility
        for existing_record in self.expenses[normalized_category]:
            if (
                existing_record.get("amount") == record.get("amount")
                and existing_record.get("date") == record.get("date")
                and existing_record.get("description") == record.get("description")
            ):
                self.expenses[normalized_category].remove(existing_record)
                self.last_deleted = (normalized_category, existing_record)
                self.save_data()
                logger.warning("Deleted expense from %s: %s", normalized_category, existing_record)
                # NEW: Update budget alerts after deletion
                self.update_budget_alerts()
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
            # NEW: Update budget alerts after undo
            self.update_budget_alerts()
            return True

        # Then try to undo a single delete
        if self.last_deleted:
            category, record = self.last_deleted
            self.expenses.setdefault(category, []).append(record)
            self.last_deleted = None
            self.save_data()
            logger.info("Undo delete: restored %s", record)
            # NEW: Update budget alerts after undo
            self.update_budget_alerts()
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
        normalized_old_category = self.normalize_category_name(old_category)
        if (
            normalized_old_category not in self.expenses
            or old_record not in self.expenses[normalized_old_category]
        ):
            return False  # ✅ return False if nothing found

        self.expenses[normalized_old_category].remove(old_record)

        category = self.normalize_category_name(new_data.get("category", normalized_old_category))
        amount = float(new_data.get("amount", old_record.get("amount", 0)))
        date = new_data.get("date", old_record.get("date", ""))
        desc = new_data.get("description", old_record.get("description", ""))

        self.expenses.setdefault(category, []).append(
            {"amount": amount, "date": date, "description": desc}
        )
        self.save_data()
        logger.info("Updated expense from %s → %s", old_record, new_data)
        
        # NEW: Update budget alerts after update
        self.update_budget_alerts()
        
        return True

    def get_expenses_for_category(self, category):
        """Return all expenses for a given category."""
        normalized_category = self.normalize_category_name(category)
        return self.expenses.get(normalized_category, [])

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

        self.update_budget_alerts()

    def undo_clear(self):
        """Restore expenses after clear_all."""
        if hasattr(self, "last_cleared") and self.last_cleared:
            self.expenses = self.last_cleared
            self.last_cleared = None
            self.save_data()
            logger.info("Undo clear: restored all expenses")
            # NEW: Update budget alerts after undo
            self.update_budget_alerts()
            return True
        return False

    def list_expenses(self):
        """Return expenses by category (alias for get_sorted_expenses for test compatibility)."""
        return self.get_sorted_expenses()

    def get_all_expenses(self):
        """Alias for list_all_expenses for test compatibility."""
        return self.list_all_expenses()
