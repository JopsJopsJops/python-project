from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QDialog, QCalendarWidget, QLabel, QLineEdit, QHeaderView,
    QAbstractItemView, QShortcut, QListWidget, QComboBox,
    QDialogButtonBox, QTabWidget, QMainWindow, QAction,QDateEdit,
    QFileDialog
)
from PyQt5.QtGui import QFont, QKeySequence, QColor
from PyQt5.QtCore import Qt, QDate, QTimer, QPropertyAnimation
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys, os, json, csv, openpyxl
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


# ----------------------------
# Data manager (JSON storage)
# ----------------------------
class DataManager:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = {}
        self.categories = ["Food", "Medical", "Utilities", "Travel",
                           "Clothing", "Transportation", "Vehicle", "Uncategorized"]
        self.last_deleted = None
        self.load_expense()

    def load_expense(self):
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.expenses = data.get("expenses", {})
                self.categories = data.get("categories", self.categories)
        except (json.JSONDecodeError, FileNotFoundError):
            self.expenses = {}
            self.categories = ["Food", "Medical", "Utilities", "Travel",
                               "Clothing", "Transportation", "Vehicle", "Uncategorized"]

    def save_data(self):
        data = {
            "expenses": self.expenses,
            "categories": self.categories
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def add_category(self, category):
        if category not in self.categories:
            self.categories.append(category)
            self.save_data()

    def remove_category(self, category):
        if category in self.categories:
            self.categories.remove(category)
            self.save_data()

    def add_expense(self, category, amount, date, description):
        new_record = {
            "amount": float(amount),
            "date": date,
            "description": description
        }
        self.expenses.setdefault(category, []).append(new_record)
        self.save_data()

    def delete_expense(self, category, record):
        if category in self.expenses and record in self.expenses[category]:
            self.expenses[category].remove(record)
            self.last_deleted = (category, record)
            if not self.expenses[category]:
                del self.expenses[category]
            self.save_data()
            return True
        return False

    def undo_delete(self):
        if self.last_deleted:
            category, record = self.last_deleted
            self.expenses.setdefault(category, []).append(record)
            self.last_deleted = None
            self.save_data()
            return True
        return False

    def get_sorted_expenses(self):
        """Return expenses dict with records sorted by date (asc)."""
        return {
            cat: sorted(records,
                        key=lambda r: datetime.strptime(r["date"], "%Y-%m-%d"))
            for cat, records in self.expenses.items()
        }

    def get_category_subtotals(self):
        return {category: sum(rec["amount"] for rec in records)
                for category, records in self.expenses.items()}

    def search_expenses(self, keyword):
        results = []
        for category, records in self.expenses.items():
            for record in records:
                if keyword.lower() in record["description"].lower():
                    results.append((category, record))
        return results

    def get_all_categories(self):
        return list(self.expenses.keys())


# ----------------------------
# Helpers
# ----------------------------
class NumericTableWidgetItem(QTableWidgetItem):
    """Custom item that sorts numeric strings (with currency) properly."""
    def __lt__(self, other):
        # keep grand_total row pinned (if applied using UserRole)
        try:
            if self.data(Qt.UserRole) == "grand_total":
                return False
            if other.data(Qt.UserRole) == "grand_total":
                return True
        except Exception:
            pass

        try:
            a = float(self.text().replace("₱", "").replace(",", ""))
            b = float(other.text().replace("₱", "").replace(",", ""))
            return a < b
        except Exception:
            return super().__lt__(other)


# ----------------------------
# Category management dialog
# ----------------------------
class CategoryDialog(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent = parent
        self.setWindowTitle("Manage Categories")
        self.resize(360, 400)

        self.layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.data_manager.categories)
        self.layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.remove_btn = QPushButton("Remove")
        self.close_btn = QPushButton("Close")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.close_btn)
        self.layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_category)
        self.remove_btn.clicked.connect(self.remove_category)
        self.close_btn.clicked.connect(self.accept)

    def add_category(self):
        name, ok = QInputDialog.getText(self, "Add Category", "Category name:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.data_manager.categories:
                self.data_manager.categories.append(name)
                self.list_widget.addItem(name)
                self.data_manager.save_data()
                if self.parent:
                    self.parent.refresh_category_dropdowns()
                    # refresh dashboard if present
                    self._refresh_dashboards()
            else:
                QMessageBox.warning(self, 'Duplicate', f"'{name}' already exists.")

    def remove_category(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a category to remove.")
            return

        category = selected.text()
        if category == "Uncategorized":
            QMessageBox.warning(self, "Not Allowed", "'Uncategorized' cannot be removed.")
            return

        if category not in self.data_manager.categories:
            QMessageBox.warning(self, "Error", f"'{category}' is not in the category list.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Deleting '{category}' will move all its expenses into 'Uncategorized'. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        if category in self.data_manager.expenses:
            uncategorized = self.data_manager.expenses.setdefault("Uncategorized", [])
            uncategorized.extend(self.data_manager.expenses.pop(category))

        try:
            self.data_manager.categories.remove(category)
        except ValueError:
            pass

        self.data_manager.save_data()
        if self.parent:
            self.parent.refresh_category_dropdowns()
            self.parent.render_table(self.data_manager.get_sorted_expenses())
        self._refresh_dashboards()

    def _refresh_dashboards(self):
        for w in QApplication.topLevelWidgets():
            for dash in w.findChildren(DashboardWidget):
                dash.update_dashboard()



# ----------------------------
# Add / Edit Expense dialog
# ----------------------------
class AddExpenseDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add / Edit Expense")
        self.resize(380, 380)

        layout = QVBoxLayout(self)

        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(categories)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setSelectedDate(QDate.currentDate())

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Enter description")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_dropdown)
        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.calendar_widget)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(button_box)

    def get_data(self):
        try:
            return {
                "category": self.category_dropdown.currentText(),
                "amount": float(self.amount_input.text()),
                "date": self.calendar_widget.selectedDate().toString("yyyy-MM-dd"),
                "description": self.desc_input.text()
            }
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return None


# ----------------------------
# Dashboard widget (embedded in main UI)
# ----------------------------
class DashboardWidget(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.summary_tab = QWidget()
        self.charts_tab = QWidget()
        self.trends_tab = QWidget()

        self.tabs.addTab(self.summary_tab, "Summary")
        self.tabs.addTab(self.charts_tab, "Charts")
        self.tabs.addTab(self.trends_tab, "Trends")

        self.init_summary_tab()
        self.init_charts_tab()
        self.init_trends_tab()

        self.update_dashboard()

    # Summary
    def init_summary_tab(self):
        layout = QVBoxLayout()
        self.summary_tab.setLayout(layout)

        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["Category", "Subtotal (₱)"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.summary_table)

        self.total_label = QLabel("Grand Total: ₱0.00")
        self.total_label.setFont(QFont("Verdana", 12, QFont.Bold))
        layout.addWidget(self.total_label)

    def update_summary_tab(self):
        data = self.data_manager.get_sorted_expenses()
        self.summary_table.setRowCount(0)
        total_all = 0
        for category, records in data.items():
            subtotal = sum(rec.get("amount", 0.0) or 0.0 for rec in records)
            row = self.summary_table.rowCount()
            self.summary_table.insertRow(row)
            self.summary_table.setItem(row, 0, QTableWidgetItem(category))
            self.summary_table.setItem(row, 1, NumericTableWidgetItem(f"{subtotal:.2f}"))
            total_all += subtotal

        # grand total row
        row = self.summary_table.rowCount()
        self.summary_table.insertRow(row)
        grand_item = QTableWidgetItem("Grand Total")
        grand_item.setFont(QFont("Verdana", 11, QFont.Bold))
        self.summary_table.setItem(row, 0, grand_item)
        grand_amt = QTableWidgetItem(f"₱{total_all:,.2f}")
        grand_amt.setFont(QFont("Verdana", 11, QFont.Bold))
        self.summary_table.setItem(row, 1, grand_amt)
        self.total_label.setText(f"Grand Total: ₱{total_all:,.2f}")

    # Charts
    def init_charts_tab(self):
        layout = QHBoxLayout()
        self.charts_tab.setLayout(layout)

        self.pie_fig, self.pie_ax = plt.subplots()
        self.pie_canvas = FigureCanvas(self.pie_fig)
        layout.addWidget(self.pie_canvas)

        self.bar_fig, self.bar_ax = plt.subplots()
        self.bar_canvas = FigureCanvas(self.bar_fig)
        layout.addWidget(self.bar_canvas)

    def update_charts_tab(self):
        data = self.data_manager.get_sorted_expenses()
        categories = []
        amounts = []
        for category, records in data.items():
            subtotal = sum(rec.get("amount", 0.0) or 0.0 for rec in records)
            if subtotal > 0:
                categories.append(category)
                amounts.append(subtotal)

        # Pie chart (top 5 + others)
        self.pie_ax.clear()
        if amounts:
            sorted_data = sorted(zip(categories, amounts), key=lambda x: x[1], reverse=True)
            cats_sorted, amts_sorted = zip(*sorted_data)
            top_categories = list(cats_sorted[:5])
            top_amounts = list(amts_sorted[:5])
            if len(cats_sorted) > 5:
                other_total = sum(amts_sorted[5:])
                top_categories.append("Others")
                top_amounts.append(other_total)
            explode = [0.05 if a < (sum(amts_sorted) * 0.01) else 0 for a in top_amounts]
            self.pie_ax.pie(top_amounts, labels=top_categories, autopct="%1.1f%%", startangle=90, explode=explode)
            self.pie_ax.axis("equal")
        self.pie_canvas.draw()

        # Bar (sorted high->low)
        self.bar_ax.clear()
        if amounts:
            sorted_data = sorted(zip(categories, amounts), key=lambda x: x[1], reverse=True)
            cats, amts = zip(*sorted_data)
            self.bar_ax.bar(cats, amts)
            self.bar_ax.set_ylabel("Amount (₱)")
            self.bar_ax.set_title("Spending by Category (High → Low)")
            self.bar_ax.tick_params(axis='x', rotation=30)
        self.bar_canvas.draw()

    # Trends
    def init_trends_tab(self):
        layout = QVBoxLayout()
        self.trends_tab.setLayout(layout)

        self.trend_fig, self.trend_ax = plt.subplots()
        self.trend_canvas = FigureCanvas(self.trend_fig)
        layout.addWidget(self.trend_canvas)

    def update_trends_tab(self):
        data = self.data_manager.get_sorted_expenses()
        monthly_totals = {}
        for records in data.values():
            for rec in records:
                date = rec.get("date", "")
                amount = rec.get("amount", 0.0) or 0.0
                if date:
                    month = date[:7]  # YYYY-MM
                    monthly_totals[month] = monthly_totals.get(month, 0) + amount

        months = sorted(monthly_totals.keys())
        totals = [monthly_totals[m] for m in months]

        self.trend_ax.clear()
        if months:
            self.trend_ax.plot(months, totals, marker="o")
            self.trend_ax.set_title("Expense Trend Over Time")
            self.trend_ax.set_xlabel("Month")
            self.trend_ax.set_ylabel("Total Expenses")
            self.trend_ax.tick_params(axis='x', rotation=45)
        self.trend_canvas.draw()

    def update_dashboard(self):
        self.update_summary_tab()
        self.update_charts_tab()
        self.update_trends_tab()


# ----------------------------
# Expense tracker widget (uses DataManager)
# ----------------------------
class ExpenseTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.initUI()
        self.show_expense()

    def initUI(self):
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(400, 100, 900, 600)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Category", "Amount", "Date", "Description", "Actions"])
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().sectionClicked.connect(self.on_table_sorted)

        # Buttons row
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_expense)
        btn_layout.addWidget(add_btn)

        show_exp_btn = QPushButton("Show Expenses")
        show_exp_btn.clicked.connect(self.show_expense)
        btn_layout.addWidget(show_exp_btn)

        totals_btn = QPushButton("Totals")
        totals_btn.clicked.connect(self.show_total_expense)
        btn_layout.addWidget(totals_btn)

        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_last_delete)
        self.undo_btn.setEnabled(False)
        btn_layout.addWidget(self.undo_btn)

        manage_categories_btn = QPushButton("Manage Categories")
        manage_categories_btn.clicked.connect(self.open_category_dialog)
        btn_layout.addWidget(manage_categories_btn)

        # Dashboard shortcut button (if running inside MainWindow tabs this will switch)
        dashboard_btn = QPushButton("Dashboard")
        dashboard_btn.clicked.connect(self.go_to_dashboard)
        btn_layout.addWidget(dashboard_btn)

        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.exit_mode)
        btn_layout.addWidget(exit_btn)

        layout.addLayout(btn_layout)

        # Search row
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search description...")
        self.search_input.returnPressed.connect(self.search_expenses)
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_expenses)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)
        shortcut = QShortcut(QKeySequence("Escape"), self)
        shortcut.activated.connect(self.clear_search)
        layout.addLayout(search_layout)

        layout.addWidget(self.table)

        self.summary_label = QLabel("Total: ₱0.00")
        self.summary_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.summary_label.setStyleSheet("color: black;")
        self.summary_label.setFont(QFont("Verdana", 14, QFont.Bold))
        layout.addWidget(self.summary_label)

        self.setLayout(layout)

    # ---------- navigation ----------
    def go_to_dashboard(self):
        # finds a MainWindow (if present) and shows its dashboard tab
        for w in QApplication.topLevelWidgets():
            if isinstance(w, MainWindow):
                w.tabs.setCurrentWidget(w.dashboard_tab)
                w.dashboard.update_dashboard()
                break

    # ---------- Category dialog ----------
    def open_category_dialog(self):
        dialog = CategoryDialog(self.data_manager, self)
        dialog.exec_()
        self.refresh_category_dropdowns()
        self.show_expense()
        self._refresh_dashboards()

    # ---------- add / edit / delete ----------
    def add_expense(self):
        dialog = AddExpenseDialog(self.data_manager.categories, self)
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                self.data_manager.add_expense(data["category"], data["amount"], data["date"], data["description"])
                self.render_table(self.data_manager.get_sorted_expenses())
                self._refresh_dashboards()
               

    def edit_expense(self, category, record):
        dialog = AddExpenseDialog(self.data_manager.categories, self)
        dialog.setWindowTitle("Edit Expense")
        dialog.amount_input.setText(str(record["amount"]))
        date_obj = QDate.fromString(record["date"], "yyyy-MM-dd")
        if date_obj.isValid():
            dialog.calendar_widget.setSelectedDate(date_obj)
        dialog.desc_input.setText(record["description"])
        index = dialog.category_dropdown.findText(category)
        if index >= 0:
            dialog.category_dropdown.setCurrentIndex(index)

        if dialog.exec_():
            new_data = dialog.get_data()
            if new_data:
                # replace
                try:
                    self.data_manager.expenses[category].remove(record)
                except Exception:
                    pass
                self.data_manager.expenses.setdefault(new_data["category"], []).append(new_data)
                self.data_manager.save_data()
                self.render_table(self.data_manager.get_sorted_expenses())
                self._refresh_dashboards()
              

    def delete_expense(self, category, record):
        if self.data_manager.delete_expense(category, record):
            QMessageBox.information(self, "Deleted", "Expense deleted successfully.")
            self.render_table(self.data_manager.get_sorted_expenses())
            self.undo_btn.setEnabled(True)
            self._refresh_dashboards()
         

    def undo_last_delete(self):
        if self.data_manager.undo_delete():
            QMessageBox.information(self, "Restored", "Last deleted expense restored.")
            self.show_expense()
            self.undo_btn.setEnabled(False)
            self._refresh_dashboards()
        else:
            QMessageBox.information(self, "Undo", "No expense to restore.")

    # ---------- search / show / totals ----------
    def search_expenses(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self.show_expense()
            return
        results = self.data_manager.search_expenses(keyword)
        self.render_table(results, is_search=True)

    def show_expense(self):
        expenses = self.data_manager.get_sorted_expenses()
        if not expenses:
            QMessageBox.information(self, "No Data", "There are no expenses to display.")
        self.render_table(expenses)
        # keep date-sorted default
        self.table.sortItems(2)

    def show_total_expense(self):
        expenses = self.data_manager.get_sorted_expenses()
        self.render_table(expenses, show_totals=True)
        # sort by amount to see ordering (but grand total will be pinned)
        self.table.sortItems(1, Qt.AscendingOrder)
        self.pin_grand_total_row()

    # ---------- table rendering ----------
    def render_table(self, data, show_totals=False, is_search=False):
        """Renders the table.
        - is_search: data is list of (category, record) tuples (individual rows)
        - show_totals: show each category subtotal (only) + Grand Total pinned bottom
        - else: show individual records with action buttons
        """
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        total_all = 0.0

        # ensure 5 columns available
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Category", "Amount", "Date", "Description", "Actions"])

        def add_action_row(category, record):
            row = self.table.rowCount()
            self.table.insertRow(row)
            amount = record.get("amount", 0.0) or 0.0
            date = record.get("date", "")
            description = record.get("description", "")

            self.table.setItem(row, 0, QTableWidgetItem(category))
            self.table.setItem(row, 1, NumericTableWidgetItem(f"{amount:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            self.table.setItem(row, 3, QTableWidgetItem(description))

            action_widget = QWidget()
            layout = QHBoxLayout(action_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            edit_btn.clicked.connect(lambda _, c=category, r=record: self.edit_expense(c, r))
            delete_btn.clicked.connect(lambda _, c=category, r=record: self.delete_expense(c, r))

            layout.addWidget(edit_btn)
            layout.addWidget(delete_btn)
            action_widget.setLayout(layout)

            self.table.setCellWidget(row, 4, action_widget)

        def add_total_row(category_name, subtotal, is_grand=False):
            row = self.table.rowCount()
            self.table.insertRow(row)
            if is_grand:
                item_cat = QTableWidgetItem("Grand Total")
                item_amt = NumericTableWidgetItem(f"₱{subtotal:,.2f}")
                item_desc = QTableWidgetItem("")
                item_action = QTableWidgetItem("")
            else:
                item_cat = QTableWidgetItem(category_name)
                item_amt = NumericTableWidgetItem(f"₱{subtotal:,.2f}")
                item_desc = QTableWidgetItem("Subtotal")
                item_action = QTableWidgetItem("")

            font = QFont("Verdana", 12, QFont.Bold) if is_grand else QFont("Verdana", 11, QFont.Bold)
            bg_color = Qt.yellow if is_grand else QColor.fromHsl(183, int(0.42 * 255), int(0.93 * 255))

            for item in [item_cat, item_amt, item_desc, item_action]:
                item.setFont(font)
                item.setBackground(bg_color)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

            self.table.setItem(row, 0, item_cat)
            self.table.setItem(row, 1, item_amt)
            self.table.setItem(row, 2, QTableWidgetItem(""))
            self.table.setItem(row, 3, QTableWidgetItem(""))
            self.table.setItem(row, 4, QTableWidgetItem(""))

            if is_grand:
                item_cat.setData(Qt.UserRole, "grand_total")
                item_amt.setData(Qt.UserRole, "grand_total")
                self.table.setSpan(row, 2, 1, 3)

        if show_totals:
            # show only categories subtotals and grand total
            for category in sorted(data.keys()):
                records = data.get(category, [])
                subtotal = sum(rec.get("amount", 0.0) or 0.0 for rec in records)
                add_total_row(category, subtotal)
                total_all += subtotal
            add_total_row("Grand Total", total_all, is_grand=True)

        elif is_search:
            for category, record in data:
                add_action_row(category, record)
                total_all += record.get("amount", 0.0) or 0.0

        else:
            # default: full details with action buttons
            for category in sorted(data.keys()):
                records = data.get(category, [])
                for record in records:
                    add_action_row(category, record)
                    total_all += record.get("amount", 0.0) or 0.0

        if self.table.rowCount() == 0:
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem("No data available"))
            self.table.item(0, 0).setFont(QFont("Verdana", 12, QFont.Bold))
            self.table.setSpan(0, 0, 1, self.table.columnCount())

        self.summary_label.setText(f"Total: ₱{total_all:,.2f}")

        # sorting and pin grand total to bottom if present
        self.table.setSortingEnabled(True)
        if show_totals:
            self.pin_grand_total_row()

    # ---------- utilities ----------
    def refresh_category_dropdowns(self):
        # update open AddExpenseDialog instances (they are top-level when exec_ runs)
        for widget in QApplication.topLevelWidgets():
            for dlg in widget.findChildren(AddExpenseDialog):
                dlg.category_dropdown.clear()
                dlg.category_dropdown.addItems(self.data_manager.categories)

    def _refresh_dashboards(self):
        for w in QApplication.topLevelWidgets():
            for dash in w.findChildren(DashboardWidget):
                dash.update_dashboard()

    # ---------- labels, animations ----------
    def clear_search(self):
        self.search_input.clear()
        self.show_expense()

        self.summary_label.setText("Search cleared ✅ Showing all expenses")
        self.summary_label.setStyleSheet("color: green; font-weight: bold;")
        QTimer.singleShot(2000, self.fade_label)

    def update_summary_label(self):
        expenses = self.data_manager.get_sorted_expenses()
        total_all = sum(rec["amount"] for records in expenses.values() for rec in records)
        self.summary_label.setText(f"Total: ₱{total_all:,.2f}")

    def fade_label(self, fade_out_duration=600, fade_in_duration=500):
        effect = QGraphicsOpacityEffect(self.summary_label)
        self.summary_label.setGraphicsEffect(effect)

        fade_out = QPropertyAnimation(effect, b"opacity")
        fade_out.setDuration(fade_out_duration)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)

        def on_fade_out_finished():
            self.update_summary_label()
            self.summary_label.setStyleSheet("color: black; font-weight: bold;")
            fade_in = QPropertyAnimation(effect, b"opacity")
            fade_in.setDuration(fade_in_duration)
            fade_in.setStartValue(0)
            fade_in.setEndValue(1)
            fade_in.start()
            self._fade_in = fade_in

        fade_out.finished.connect(on_fade_out_finished)
        fade_out.start()
        self._fade_out = fade_out

    # ---------- sorting helpers ----------
    def on_table_sorted(self, idx):
        # after any header click, keep grand total pinned if present
        self.pin_grand_total_row()

    def pin_grand_total_row(self):
        rows = self.table.rowCount()
        grand_rows = [r for r in range(rows)
                      if self.table.item(r, 0) and self.table.item(r, 0).data(Qt.UserRole) == "grand_total"]
        if not grand_rows:
            return
        grand_row = grand_rows[0]
        if grand_row != rows - 1:
            # take items and widgets from the grand row, move them to bottom
            items = [self.table.takeItem(grand_row, c) for c in range(self.table.columnCount())]
            widgets = [self.table.cellWidget(grand_row, c) for c in range(self.table.columnCount())]
            self.table.removeRow(grand_row)
            new_row = self.table.rowCount()
            self.table.insertRow(new_row)
            for c, it in enumerate(items):
                if it is not None:
                    # restore item
                    self.table.setItem(new_row, c, it)
                # move widget (if any)
                w = widgets[c]
                if w is not None:
                    self.table.setCellWidget(new_row, c, w)
            # span the remainder columns for the grand row (date/desc/actions)
            try:
                self.table.setSpan(new_row, 2, 1, 3)
            except Exception:
                pass
        else:
            # ensure span exists
            try:
                self.table.setSpan(grand_row, 2, 1, 3)
            except Exception:
                pass

    # ---------- exit ----------
    def exit_mode(self):
        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to save and exit?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.data_manager.save_data()
            QMessageBox.information(self, "Save successful", "Thank you for using Expense Tracker.")
            QApplication.quit()


# ----------------------------
# Main Application Window (tabs: Expenses, Dashboard, Reports)
# ----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(120, 120, 1100, 700)

        # Tabs widget as central
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Expenses Tab
        self.expenses_tab = QWidget()
        expenses_layout = QVBoxLayout(self.expenses_tab)
        self.expense_tracker = ExpenseTracker()
        expenses_layout.addWidget(self.expense_tracker)
        self.tabs.addTab(self.expenses_tab, "Expenses")

        # Dashboard Tab
        self.dashboard_tab = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_tab)
        self.dashboard = DashboardWidget(self.expense_tracker.data_manager)
        dash_layout.addWidget(self.dashboard)
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # Reports Tab (with grouped export buttons)
        self.setup_reports_tab()

        # Menu bar
        self.create_menus()

        # Refresh dashboard on tab switch
        self.tabs.currentChanged.connect(self.refresh_dashboard_on_switch)

    def create_menus(self):
        menubar = self.menuBar()

        # ---- File Menu ----
        file_menu = menubar.addMenu("File")

        # Import submenu
        import_menu = file_menu.addMenu("Import")
        import_csv_action = QAction("Import CSV", self)
        import_csv_action.triggered.connect(self.import_from_csv)
        import_excel_action = QAction("Import Excel", self)
        import_excel_action.triggered.connect(self.import_from_excel)
        import_menu.addAction(import_csv_action)
        import_menu.addAction(import_excel_action)

        # Export submenu
        export_menu = file_menu.addMenu("Export")
        export_excel_csv_action = QAction("Export to Excel/CSV", self)
        export_excel_csv_action.triggered.connect(self.export_to_excel_or_csv)
        export_pdf_action = QAction("Export to PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        export_menu.addAction(export_excel_csv_action)
        export_menu.addAction(export_pdf_action)

        # Exit option
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ---- View Menu ----
        view_menu = menubar.addMenu("View")
        view_menu.addAction(QAction("Show Expenses", self, triggered=lambda: self.tabs.setCurrentWidget(self.expenses_tab)))
        view_menu.addAction(QAction("Show Dashboard", self, triggered=lambda: self.tabs.setCurrentWidget(self.dashboard_tab)))
        view_menu.addAction(QAction("Show Reports", self, triggered=lambda: self.tabs.setCurrentWidget(self.reports_tab)))

        # ---- Help Menu ----
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(QAction("About", self))

      # --- Reports Tab ---
    def setup_reports_tab(self):
        self.reports_tab = QWidget()
        reports_layout = QVBoxLayout(self.reports_tab)

        title = QLabel("Reports & Exports")
        title.setFont(QFont("Verdana", 14, QFont.Bold))
        reports_layout.addWidget(title)

        # --- Filters ---
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))  # default: last 30 days
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)

        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All")
        self.category_filter.addItems(self.expense_tracker.data_manager.get_all_categories())
        filter_layout.addWidget(self.category_filter)

        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.update_report_view)
        filter_layout.addWidget(apply_filter_btn)

        reports_layout.addLayout(filter_layout)

        # --- Summary Stats ---
        self.summary_label = QLabel("Summary: No data")
        self.summary_label.setFont(QFont("Arial", 11))
        reports_layout.addWidget(self.summary_label)

        # --- Table Preview ---
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(["Category", "Amount", "Date", "Description"])
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        reports_layout.addWidget(self.report_table)

        # --- Export Buttons ---
        btn_layout = QHBoxLayout()
        btn_excel_csv = QPushButton("Export to Excel/CSV")
        btn_excel_csv.clicked.connect(self.export_to_excel_or_csv)

        btn_pdf = QPushButton("Export to PDF")
        btn_pdf.clicked.connect(self.export_to_pdf)

        btn_layout.addWidget(btn_excel_csv)
        btn_layout.addWidget(btn_pdf)
        reports_layout.addLayout(btn_layout)

        reports_layout.addStretch()
        self.tabs.addTab(self.reports_tab, "Reports")

    def update_report_view(self):
        """Update the table + summary stats based on filters"""
        from datetime import datetime

        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        selected_category = self.category_filter.currentText()

        expenses = self.expense_tracker.data_manager.get_sorted_expenses()

        filtered = []
        for category, records in expenses.items():
            if selected_category != "All" and category != selected_category:
                continue
            for rec in records:
                try:
                    rec_date = datetime.strptime(rec.get("date", ""), "%Y-%m-%d").date()
                except Exception:
                    continue
                if start <= rec_date <= end:
                    rec_with_cat = rec.copy()
                    rec_with_cat["category"] = category
                    filtered.append(rec_with_cat)

        # --- Update Table ---
        self.report_table.setRowCount(len(filtered))
        for row, rec in enumerate(filtered):
            self.report_table.setItem(row, 0, QTableWidgetItem(rec.get("category", "")))
            self.report_table.setItem(row, 1, QTableWidgetItem(str(rec.get("amount", 0))))
            self.report_table.setItem(row, 2, QTableWidgetItem(rec.get("date", "")))
            self.report_table.setItem(row, 3, QTableWidgetItem(rec.get("description", "")))

        # --- Summary Stats ---
        if filtered:
            total = sum(float(rec.get("amount", 0)) for rec in filtered)
            categories = {}
            for rec in filtered:
                categories[rec["category"]] = categories.get(rec["category"], 0) + float(rec.get("amount", 0))

            highest = max(categories, key=categories.get)
            lowest = min(categories, key=categories.get)
            avg = total / len(filtered)

            self.summary_label.setText(
                f"Summary: Total = {total:.2f} | Highest = {highest} ({categories[highest]:.2f}) | "
                f"Lowest = {lowest} ({categories[lowest]:.2f}) | Avg/Entry = {avg:.2f}"
            )
        else:
            self.summary_label.setText("Summary: No data in this range")


    def refresh_dashboard_on_switch(self, index):
        if self.tabs.widget(index) == self.dashboard_tab:
            self.dashboard.update_dashboard()

    # --- Export functions ---

    def get_filtered_expenses(self):
        """Helper: returns expenses based on current filters"""
        from datetime import datetime
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        selected_category = self.category_filter.currentText()

        expenses = self.expense_tracker.data_manager.get_sorted_expenses()
        filtered = []

        for category, records in expenses.items():
            if selected_category != "All" and category != selected_category:
                continue
            for rec in records:
                try:
                    rec_date = datetime.strptime(rec.get("date", ""), "%Y-%m-%d").date()
                except Exception:
                    continue
                if start <= rec_date <= end:
                    filtered.append({
                        "Category": rec.get("category", category),
                        "Amount": rec.get("amount", 0.0),
                        "Date": rec.get("date", ""),
                        "Description": rec.get("description", "")
                    })
        return filtered

    def export_to_excel_or_csv(self):
        import pandas as pd
        from PyQt5.QtWidgets import QFileDialog, QMessageBox

        data = self.get_filtered_expenses()
        if not data:
            QMessageBox.information(self, "Export", "No expenses to export.")
            return

        df = pd.DataFrame(data)
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "expenses.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )

        if file_path:
            try:
                if selected_filter.startswith("Excel"):
                    if not file_path.endswith(".xlsx"):
                        file_path += ".xlsx"
                    df.to_excel(file_path, index=False)
                else:  # CSV selected
                    if not file_path.endswith(".csv"):
                        file_path += ".csv"
                    df.to_csv(file_path, index=False)

                QMessageBox.information(self, "Export", f"Exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))

    def export_to_pdf(self):
        from fpdf import FPDF
        from PyQt5.QtWidgets import QFileDialog, QMessageBox

        data = self.get_filtered_expenses()
        if not data:
            QMessageBox.information(self, "Export", "No expenses to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "expenses.pdf", "PDF Files (*.pdf)")
        if file_path:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Expense Report", ln=True, align="C")
                pdf.ln(10)

                col_widths = [40, 30, 40, 80]
                headers = ["Category", "Amount", "Date", "Description"]

                # Header row
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, header, border=1)
                pdf.ln()

                # Data rows
                for rec in data:
                    pdf.cell(col_widths[0], 10, rec["Category"], border=1)
                    pdf.cell(col_widths[1], 10, str(rec["Amount"]), border=1)
                    pdf.cell(col_widths[2], 10, rec["Date"], border=1)
                    pdf.cell(col_widths[3], 10, rec["Description"], border=1)
                    pdf.ln()

                pdf.output(file_path)
                QMessageBox.information(self, "Export", f"Exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Error", str(e))


    def import_from_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Import from CSV", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            try:
                with open(file_name, newline="", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        expense = {
                            "date": row.get("Date", ""),
                            "category": row.get("Category", ""),
                            "amount": row.get("Amount", ""),
                            "description": row.get("Description", "")
                        }
                        self.data_manager.add_expense(expense["category"], expense["amount"], expense["date"], expense["description"])
                self.data_manager.load_expense()
                QMessageBox.information(self, "Import Successful", "Expenses imported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"Error: {e}")   

    def import_from_excel(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Import from Excel", "", "Excel Files (*.xlsx);;All Files (*)", options=options
        )
        if file_name:
            try:
                wb = openpyxl.load_workbook(file_name)
                sheet = wb.active

                # Expecting header in row 1: Date | Category | Amount | Description
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    expense = {
                        "date": row[0] if row[0] else "",
                        "category": row[1] if row[1] else "",
                        "amount": row[2],
                        "description": row[3] if row[3] else ""
                    }
                    # Convert amount to float, handle errors
                    try:
                        amount = float(expense["amount"])
                    except (TypeError, ValueError):
                        amount = 0.0
                    self.data_manager.add_expense(expense["category"], amount, expense["date"], expense["description"])

                self.data_manager.load_expense()
                QMessageBox.information(self, "Import Successful", "Expenses imported successfully from Excel!")

            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"Error: {e}")

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
