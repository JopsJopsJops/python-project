from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QInputDialog, QMessageBox,
    QListWidget, QPushButton, QComboBox, QLineEdit, QLabel,
    QDialogButtonBox, QCalendarWidget)
from expense_tracker_app.data_manager import DataManager

import logging
logger = logging.getLogger(__name__)


class CategoryDialog(QDialog):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent = parent
        self.setWindowTitle("Manage Categories")
        self.resize(360, 400)

        self.layout = QVBoxLayout(self)

        self.list_widget = QListWidget()

        # Handle both DataManager objects and test lists
        if isinstance(self.data_manager, list):
            # Test mode - data_manager is just a list of categories
            self.list_widget.addItems(self.data_manager)
        else:
            # Normal mode - data_manager is DataManager instance
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
        # Use QInputDialog instead of QMessageBox for text input
        name, ok = QInputDialog.getText(self, "Add Category", "Category name:")
        if ok and name.strip():
            name = name.strip()
            if isinstance(self.data_manager, list):
                # Test mode
                if name not in self.data_manager:
                    self.data_manager.append(name)
                    self.list_widget.addItem(name)
            else:
                # Normal mode
                if name not in self.data_manager.categories:
                    self.data_manager.categories.append(name)
                    self.list_widget.addItem(name)
                    self.data_manager.save_data()
                    if self.parent:
                        try:
                            self.parent.refresh_category_dropdowns()
                            self.parent.render_table(
                                self.data_manager.get_sorted_expenses())
                        except Exception:
                            pass
                        self._refresh_dashboards()
            # Show duplicate warning if needed
            if (isinstance(self.data_manager, list) and name in self.data_manager) or \
               (not isinstance(self.data_manager, list) and name in self.data_manager.categories):
                QMessageBox.warning(self, 'Duplicate',
                                    f"'{name}' already exists.")

    def remove_category(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a category to remove.")
            return

        category = selected.text()
        if category == "Uncategorized":
            QMessageBox.warning(self, "Not Allowed",
                                "'Uncategorized' cannot be removed.")
            return

        if category not in self.data_manager.categories:
            QMessageBox.warning(
                self, "Error", f"'{category}' is not in the category list.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Deleting '{category}' will move all its expenses into 'Uncategorized'. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.No:
            return

        # ✅ Always ensure 'Uncategorized' exists
        if "Uncategorized" not in self.data_manager.categories:
            self.data_manager.categories.append("Uncategorized")

        if category in self.data_manager.expenses:
            uncategorized = self.data_manager.expenses.setdefault(
                "Uncategorized", []
            )
            uncategorized.extend(self.data_manager.expenses.pop(category))

        try:
            self.data_manager.categories.remove(category)
        except ValueError:
            pass

        self.data_manager.save_data()
        if self.parent:
            try:
                self.parent.refresh_category_dropdowns()
                self.parent.render_table(
                    self.data_manager.get_sorted_expenses())
            except Exception:
                pass
        self._refresh_dashboards()

    def _refresh_dashboards(self):
        # avoid importing DashboardWidget to prevent circular import;
        # instead search for widgets with update_dashboard method
        from PyQt5.QtWidgets import QApplication, QWidget
        for w in QApplication.topLevelWidgets():
            for child in w.findChildren(QWidget):
                if hasattr(child, "update_dashboard"):
                    try:
                        child.update_dashboard()
                    except Exception:
                        pass


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

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
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
            QMessageBox.warning(self, "Invalid Input",
                                "Please enter a valid amount.")
            return None

    def validate_inputs(self):
        """Validate dialog inputs for testing."""
        try:
            amount = float(self.amount_input.text())
            if amount <= 0:
                return False
            if not self.desc_input.text().strip():
                return False
            return True
        except ValueError:
            return False
