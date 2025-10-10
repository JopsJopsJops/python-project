import csv
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem,
                             QDialog, QCalendarWidget, QLabel, QLineEdit, QHeaderView,
                             QAbstractItemView)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate
from datetime import datetime


# --- Refactored DataManager Class ---
class DataManager:
    """Manages the storage and retrieval of expense data."""

    def __init__(self, filename="expenses.csv"):
        self.filename = filename
        self.expenses = self.import_expenses()
        self.last_deleted = None

    def import_expenses(self):
        """Loads expenses from a CSV file into a dictionary."""
        expenses = {}
        try:
            with open(self.filename, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = row["category"]
                    # Use a list to store multiple records for a category
                    expenses.setdefault(category, []).append({
                        "amount": float(row["amount"]),
                        "date": row["date"],
                        "description": row["description"]
                    })
        except FileNotFoundError:
            # Return an empty dictionary if the file doesn't exist
            return {}
        except (ValueError, KeyError) as e:
            # Handle potential errors during data import
            print(f"Error importing CSV data: {e}. Starting with an empty dataset.")
            return {}
        return expenses

    def export_expenses(self):
        """Saves all expenses from the dictionary to a CSV file."""
        with open(self.filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["category", "amount", "date", "description"])
            writer.writeheader()
            for category, records in self.expenses.items():
                for record in records:
                    # Write each expense as a row in the CSV
                    writer.writerow({"category": category, **record})

    def add_expense(self, category, amount, date, description):
        """Adds a new expense and saves it to the file."""
        new_record = {
            "amount": float(amount),
            "date": date,
            "description": description
        }
        self.expenses.setdefault(category, []).append(new_record)
        self.export_expenses()

    def delete_expense(self, category, record):
        """Deletes a specific expense and stores it for potential undo."""
        if category in self.expenses and record in self.expenses[category]:
            self.expenses[category].remove(record)
            self.last_deleted = (category, record)
            # Remove category key if no expenses remain
            if not self.expenses[category]:
                del self.expenses[category]
            self.export_expenses()
            return True
        return False

    def undo_delete(self):
        """Restores the last deleted expense."""
        if self.last_deleted:
            category, record = self.last_deleted
            self.expenses.setdefault(category, []).append(record)
            self.last_deleted = None
            self.export_expenses()
            return True
        return False

    def get_sorted_expenses(self):
        """Returns all expenses sorted by date."""
        return {cat: sorted(records, key=lambda r: r["date"])
                for cat, records in self.expenses.items()}

    def get_category_subtotals(self):
        """Calculates the total expense for each category."""
        return {category: sum(rec["amount"] for rec in records)
                for category, records in self.expenses.items()}

    def search_expenses(self, keyword):
        """Finds expenses with a description containing the keyword."""
        results = []
        for category, records in self.expenses.items():
            for record in records:
                if keyword.lower() in record["description"].lower():
                    results.append((category, record))
        return results


# --- Refactored ExpenseTracker Class ---
class ExpenseTracker(QWidget):
    """The main application window for the expense tracker."""

    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.initUI()
        self.show_expense()

    def initUI(self):
        """Initializes the main UI components and layout."""
        self.setWindowTitle("Expense Tracker 💰")
        self.setGeometry(400, 100, 800, 600)

        # Main layout
        layout = QVBoxLayout(self)

        # Search bar layout
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search description...")
        self.search_input.returnPressed.connect(self.search_expenses)
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_expenses)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # Button layout
        btn_layout = QHBoxLayout()
        buttons = [
            ("Add", self.add_expense),
            ("Edit", self.edit_expense),
            ("Delete", self.delete_expense),
            ("Undo", self.undo_last_delete),
            ("Show All", self.show_expense),
            ("Show Totals", self.show_total_expense),
            ("Exit", self.exit_mode)
        ]
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        # Table widget for displaying expenses
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Category", "Amount", "Date", "Description"])
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        # Summary label
        self.summary_label = QLabel("Total: ₱0.00")
        self.summary_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.summary_label.setFont(QFont("Verdana", 14, QFont.Bold))
        layout.addWidget(self.summary_label)

        # Apply CSS styling
        self.setStyleSheet(self.get_style_sheet())

    def get_style_sheet(self):
        """Returns the CSS style sheet for the application."""
        return """
            QWidget { background-color: #f0f0f0; }
            QPushButton {
                font-family: Verdana;
                font-size: 14px;
                background-color: hsl(183, 42%, 93%);
                color: hsl(206, 88%, 57%);
                border-radius: 10px;
                padding: 5px;
                border: 2px solid blue;
            }
            QPushButton:hover {
                background-color: hsl(183, 42%, 85%);
                border: 3px solid blue;
            }
            QTableWidget {
                font-family: Verdana;
                font-size: 14px;
                color: #333;
                background-color: #fff;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #ddd;
                font-weight: bold;
                padding: 4px;
            }
        """

    def add_expense(self):
        """Opens dialogs to get new expense details and adds the expense."""
        categories = ["Food", "Medical", "Utilities", "Travel", "Clothing", "Transport", "Vehicle", "Miscellaneous"]
        category, ok = QInputDialog.getItem(self, "Add Expense", "Select category:", categories, editable=True)
        if not ok or not category: return

        try:
            amount, ok = QInputDialog.getDouble(self, "Add Expense", "Enter amount:", min=0.01)
            if not ok: return
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return

        date_dialog = CalendarDialog(initial_date=QDate.currentDate().toString("yyyy-MM-dd"))
        if date_dialog.exec_() == QDialog.Accepted:
            date = date_dialog.get_date()
        else:
            return

        description, ok = QInputDialog.getText(self, "Add Expense", "Enter description:")
        if not ok or not description: return

        self.data_manager.add_expense(category.strip(), amount, date, description.strip())
        self.show_expense()

    def edit_expense(self):
        """Edits a selected expense with new details."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Select an expense to edit.")
            return
        
        row = self.table.currentRow()
        old_category = self.table.item(row, 0).text()
        old_amount = float(self.table.item(row, 1).text())
        old_date = self.table.item(row, 2).text()
        old_description = self.table.item(row, 3).text()

        # Input new values using QInputDialog, pre-populating with old values
        new_category, ok = QInputDialog.getText(self, "Edit Expense", "Category:", text=old_category)
        if not ok: return

        new_amount, ok = QInputDialog.getDouble(self, "Edit Expense", "Amount:", value=old_amount, min=0.01)
        if not ok: return
        
        date_dialog = CalendarDialog(initial_date=old_date)
        if date_dialog.exec_() == QDialog.Accepted:
            new_date = date_dialog.get_date()
        else:
            return

        new_description, ok = QInputDialog.getText(self, "Edit Expense", "Description:", text=old_description)
        if not ok: return

        # Delete the old record and add the new one
        old_record = {"amount": old_amount, "date": old_date, "description": old_description}
        self.data_manager.delete_expense(old_category, old_record)
        self.data_manager.add_expense(new_category, new_amount, new_date, new_description)
        self.show_expense()
    
    def delete_expense(self):
        """Deletes the selected expense after user confirmation."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select an expense to delete.")
            return

        category = self.table.item(selected_row, 0).text()
        record = {
            "amount": float(self.table.item(selected_row, 1).text()),
            "date": self.table.item(selected_row, 2).text(),
            "description": self.table.item(selected_row, 3).text()
        }

        reply = QMessageBox.question(self, "Confirm", "Delete this expense?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.data_manager.delete_expense(category, record):
                self.show_expense()
            else:
                QMessageBox.warning(self, "Error", "Could not delete expense.")

    def undo_last_delete(self):
        """Restores the last deleted expense if one exists."""
        if self.data_manager.undo_delete():
            QMessageBox.information(self, "Restored", "Last deleted expense restored.")
            self.show_expense()
        else:
            QMessageBox.information(self, "No Undo", "No expense to restore.")

    def search_expenses(self):
        """Performs a search based on the keyword in the search bar."""
        keyword = self.search_input.text().strip()
        if not keyword:
            self.show_expense() # Show all expenses if search box is empty
            return
        
        results = self.data_manager.search_expenses(keyword)
        self.render_table(results, is_search=True)
    
    def show_expense(self):
        """Displays all expenses in the table, sorted by date."""
        expenses = self.data_manager.get_sorted_expenses()
        self.render_table(expenses)

    def show_total_expense(self):
        """Displays expenses with category subtotals."""
        expenses = self.data_manager.get_sorted_expenses()
        self.render_table(expenses, show_totals=True)

    def render_table(self, data, show_totals=False, is_search=False):
        """
        Renders the expense data in the table widget.
        `data` can be a dictionary of expenses or a list of search results.
        """
        self.table.setRowCount(0)
        total_all = 0

        if is_search:
            for category, record in data:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(category))
                self.table.setItem(row, 1, QTableWidgetItem(f"{record['amount']:.2f}"))
                self.table.setItem(row, 2, QTableWidgetItem(record["date"]))
                self.table.setItem(row, 3, QTableWidgetItem(record["description"]))
                total_all += record["amount"]
        else:
            for category, records in data.items():
                subtotal = 0
                for record in records:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(category))
                    self.table.setItem(row, 1, QTableWidgetItem(f"{record['amount']:.2f}"))
                    self.table.setItem(row, 2, QTableWidgetItem(record["date"]))
                    self.table.setItem(row, 3, QTableWidgetItem(record["description"]))
                    subtotal += record["amount"]
                
                if show_totals:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    # Add a total row for the category
                    self.table.setItem(row, 0, QTableWidgetItem(f"{category} Subtotal"))
                    self.table.setItem(row, 1, QTableWidgetItem(f"₱{subtotal:,.2f}"))
                    self.table.item(row, 0).setFont(QFont("Verdana", 12, QFont.Bold))
                    self.table.item(row, 1).setFont(QFont("Verdana", 12, QFont.Bold))

                total_all += subtotal

        self.summary_label.setText(f"Total: ₱{total_all:,.2f}")

    def exit_mode(self):
        """Saves data and exits the application after confirmation."""
        reply = QMessageBox.question(self, "Confirm Exit", "Are you sure you want to save and exit?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.data_manager.export_expenses()
            QMessageBox.information(self, "Save Successful", "Thank you for using Expense Tracker.")
            QApplication.quit()


# --- CalendarDialog Class ---
class CalendarDialog(QDialog):
    """A custom dialog for selecting a date from a calendar widget."""
    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.setWindowTitle("Select Date")
        self.resize(300, 250)

        layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        if initial_date:
            try:
                date_obj = datetime.strptime(initial_date, "%Y-%m-%d")
                self.calendar.setSelectedDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except ValueError:
                self.calendar.setSelectedDate(QDate.currentDate())
        else:
            self.calendar.setSelectedDate(QDate.currentDate())
        
        layout.addWidget(self.calendar)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.selected_date = None

    def accept(self):
        """Sets the selected date and closes the dialog."""
        self.selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        super().accept()
    
    def get_date(self):
        """Returns the selected date string."""
        return self.selected_date


# --- Main Entry Point ---
if __name__ == "__main__":
    app = QApplication([])
    window = ExpenseTracker()
    window.show()
    app.exec_()