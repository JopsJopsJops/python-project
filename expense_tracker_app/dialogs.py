import logging

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (QCalendarWidget, QComboBox, QDialog,
                             QDialogButtonBox, QHBoxLayout, QInputDialog,
                             QLabel, QLineEdit, QListWidget, QMessageBox,
                             QPushButton, QVBoxLayout, QSizePolicy
                             )
from PyQt5.QtGui import QColor, QFont, QTextCharFormat

from expense_tracker_app.data_manager import DataManager

logger = logging.getLogger(__name__)


class CategoryDialog(QDialog):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent = parent
        self.setWindowTitle("Manage Categories")
        self.resize(360, 400)

        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QListWidget {
                background-color: #252526;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 4px;
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QListWidget::item {
                background-color: #252526;
                color: #e0e0e0;
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)


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
        # Apply dark theme to the input dialog
        if hasattr(self, 'window') and self.window():
            input_dialog = self.findChild(QInputDialog)
            if input_dialog:
                input_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #2d2d2d;
                        color: #e0e0e0;
                    }
                    QLineEdit {
                        background-color: #252526;
                        color: #e0e0e0;
                        border: 1px solid #404040;
                        border-radius: 4px;
                        padding: 6px;
                        font-family: "Segoe UI";
                    }
                    QLabel {
                        color: #e0e0e0;
                        font-family: "Segoe UI";
                    }
                    QPushButton {
                        background-color: #007acc;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: 500;
                        font-family: "Segoe UI";
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                """)
        
        if ok and name.strip():
            name = name.strip()
            
            if isinstance(self.data_manager, list):
                # Test mode
                normalized_name = name.capitalize()  # Simple capitalization for test mode
                if normalized_name not in self.data_manager:
                    self.data_manager.append(normalized_name)
                    self.list_widget.addItem(normalized_name)  # ✅ Add normalized name
                else:
                    QMessageBox.warning(self, "Duplicate", f"'{normalized_name}' already exists.")
            else:
                # Normal mode - USE THE PROPER CATEGORY MANAGEMENT
                success, message = self.data_manager.add_category(name)
                
                if success:
                    # Refresh the list to show the CAPITALIZED version
                    self.refresh_category_list()
                    self.data_manager.save_data()
                    if self.parent:
                        try:
                            self.parent.refresh_category_dropdowns()
                            self.parent.render_table(
                                self.data_manager.get_sorted_expenses()
                            )
                        except Exception:
                            pass
                        self._refresh_dashboards()
                    
                    # Only show success message if it's a NEW category
                    if "added successfully" in message:
                        QMessageBox.information(self, "Success", message)
                    # If it's "already in your list", don't show duplicate warning
                else:
                    # Show error message for actual duplicates
                    QMessageBox.warning(self, "Duplicate", message)

    def refresh_category_list(self):
        """Refresh the category list widget with current categories"""
        self.list_widget.clear()
        if isinstance(self.data_manager, list):
            # Test mode
            self.list_widget.addItems(sorted(self.data_manager))
        else:
            # Normal mode - get the latest categories from data_manager
            self.list_widget.addItems(sorted(self.data_manager.categories))

    def remove_category(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Select a category to remove.")
            return

        category = selected.text()
        if category == "Uncategorized":
            QMessageBox.warning(
                self, "Not Allowed", "'Uncategorized' cannot be removed."
            )
            return

        if category not in self.data_manager.categories:
            QMessageBox.warning(
                self, "Error", f"'{category}' is not in the category list."
            )
            return

        # Get normalized (capitalized) version of the category
        normalized_category = self.data_manager.normalize_category_name(category)
        
        # Check if this is a duplicate that should be merged
        is_duplicate = (category != normalized_category and 
                    normalized_category in self.data_manager.categories)
        
        # Check if category has expenses
        has_expenses = (category in self.data_manager.expenses and 
                    self.data_manager.expenses[category])

        if has_expenses:
            if is_duplicate:
                # Smart merge: This is a duplicate (e.g., "food" when "Food" exists)
                reply = QMessageBox.question(
                    self,
                    "Merge Duplicate Category",
                    f"Category '{category}' appears to be a duplicate of '{normalized_category}'.\n\n"
                    f"Would you like to merge the {len(self.data_manager.expenses[category])} expense(s) "
                    f"into '{normalized_category}'?\n\n"
                    f"• <b>Merge</b> - Expenses stay organized under '{normalized_category}'\n"
                    f"• <b>Move to Uncategorized</b> - Expenses will be harder to find",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.Yes  # Default to Yes for smart merging
                )
                
                if reply == QMessageBox.Cancel:
                    return
                elif reply == QMessageBox.Yes:
                    merge_target = normalized_category
                else:
                    merge_target = "Uncategorized"
                    
            else:
                # Better UX: Step-by-step approach with clearer consequences
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
                from PyQt5.QtCore import Qt
                from PyQt5.QtGui import QFont

                dialog = QDialog(self)
                dialog.setWindowTitle(f"Remove '{category}'")
                dialog.setMinimumSize(500, 300)
                dialog.setStyleSheet("""
                    QDialog {
                        background-color: #2d2d2d;
                        color: #e0e0e0;
                    }
                    QLabel {
                        color: #e0e0e0;
                        font-family: "Segoe UI";
                    }
                    QPushButton {
                        background-color: #007acc;
                        color: white;
                        border: none;
                        padding: 12px 20px;
                        border-radius: 6px;
                        font-weight: 500;
                        font-family: "Segoe UI";
                        font-size: 12px;
                        margin: 5px;
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                    QPushButton.danger {
                        background-color: #d13438;
                    }
                    QPushButton.danger:hover {
                        background-color: #a4262c;
                    }
                    QPushButton.success {
                        background-color: #107c10;
                    }
                    QPushButton.success:hover {
                        background-color: #0e6b0e;
                    }
                    QFrame.option-frame {
                        background-color: #3c3c3c;
                        border: 1px solid #404040;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 5px;
                    }
                    QFrame.option-frame:hover {
                        background-color: #4a4a4a;
                        border-color: #007acc;
                    }
                """)

                layout = QVBoxLayout(dialog)

                # Header
                header_label = QLabel(f"🗑️ Remove '{category}'")
                header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ff6b6b;")
                header_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(header_label)

                # Warning
                warning_label = QLabel(f"This category contains {len(self.data_manager.expenses[category])} expense(s).")
                warning_label.setStyleSheet("color: #ffb86c; font-weight: bold;")
                warning_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(warning_label)

                # Options with clear benefits
                layout.addWidget(QLabel("Choose what happens to the expenses:"))

                # Option 1: Merge (Recommended)
                merge_frame = QFrame()
                merge_frame.setFrameStyle(QFrame.StyledPanel)
                merge_frame.setProperty("class", "option-frame")
                merge_layout = QVBoxLayout(merge_frame)

                merge_header = QLabel("📂 Merge into existing category")
                merge_header.setStyleSheet("font-weight: bold; color: #6bff6b;")
                merge_layout.addWidget(merge_header)

                merge_desc = QLabel("• Expenses stay organized\n• Easy to find later\n• Recommended approach")
                merge_desc.setStyleSheet("color: #b0b0b0; font-size: 11px;")
                merge_layout.addWidget(merge_desc)

                merge_btn = QPushButton("Choose Category to Merge Into")
                merge_btn.setProperty("class", "success")
                merge_btn.clicked.connect(lambda: dialog.done(1))
                merge_layout.addWidget(merge_btn)

                layout.addWidget(merge_frame)

                # Option 2: Move to Uncategorized
                uncat_frame = QFrame()
                uncat_frame.setFrameStyle(QFrame.StyledPanel)
                uncat_frame.setProperty("class", "option-frame")
                uncat_layout = QVBoxLayout(uncat_frame)

                uncat_header = QLabel("📁 Move to Uncategorized")
                uncat_header.setStyleSheet("font-weight: bold; color: #ffb86c;")
                uncat_layout.addWidget(uncat_header)

                uncat_desc = QLabel("• Expenses become harder to find\n• Use only if you can't merge\n• Not recommended")
                uncat_desc.setStyleSheet("color: #b0b0b0; font-size: 11px;")
                uncat_layout.addWidget(uncat_desc)

                uncat_btn = QPushButton("Move to Uncategorized")
                uncat_btn.clicked.connect(lambda: dialog.done(2))
                uncat_layout.addWidget(uncat_btn)

                layout.addWidget(uncat_frame)

                # Cancel option
                cancel_btn = QPushButton("❌ Keep Category (Don't Remove)")
                cancel_btn.setProperty("class", "danger")
                cancel_btn.clicked.connect(lambda: dialog.done(0))
                layout.addWidget(cancel_btn)

                # Show dialog and get result
                result = dialog.exec_()

                if result == 0:  # Cancel
                    return
                elif result == 1:  # Merge
                    merge_target = self.ask_merge_target(category)
                    if not merge_target:
                        return
                else:  # Move to Uncategorized (result == 2)
                    # ADDED: Confirmation for Move to Uncategorized
                    confirm_reply = QMessageBox.question(
                        self,
                        "Confirm Move to Uncategorized",
                        f"Are you sure you want to move {len(self.data_manager.expenses[category])} expense(s) to 'Uncategorized'?\n\n"
                        "⚠️ Expenses moved to Uncategorized will be harder to find and organize.",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No  # Default to No for safety
                    )
                    
                    if confirm_reply == QMessageBox.No:
                        return  # User changed their mind
                    
                    merge_target = "Uncategorized"
            
            # FIX: Ensure merge_target is a string, not a tuple
            if isinstance(merge_target, tuple):
                merge_target = merge_target[0]  # Take the first element if it's a tuple
            
            # Perform the removal with merge
            success, message = self.data_manager.remove_category(category, merge_target)
            
            if success:
                action = "merged into" if merge_target != "Uncategorized" else "moved to"
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Category '{category}' removed successfully.\n"
                    f"The expense(s) were {action} '{merge_target}'."
                )
            else:
                QMessageBox.warning(self, "Error", message)
                return
        else:
            # Category has NO expenses - ask for confirmation
            reply = QMessageBox.question(
                self,
                "Confirm Category Removal",
                f"Are you sure you want to remove the category '{category}'?\n\n"
                f"This category has no expenses.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Default to No for safety
            )
            
            if reply == QMessageBox.No:
                return
                
            # Perform the removal
            success, message = self.data_manager.remove_category(category)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)
                return

        # Refresh the UI
        self.refresh_category_list()
        if self.parent:
            try:
                self.parent.refresh_category_dropdowns()
                self.parent.render_table(self.data_manager.get_sorted_expenses())
            except Exception:
                pass
        self._refresh_dashboards()

    def ask_merge_target(self, category_to_remove):
        """Ask user which category to merge expenses into - FIXED to return string only"""
        # Get all available categories except the one being removed and Uncategorized
        available_categories = [
            cat for cat in self.data_manager.categories 
            if cat != category_to_remove and cat != "Uncategorized"
        ]
        
        if not available_categories:
            # No other categories available, use Uncategorized
            return "Uncategorized"  # ✅ Return string, not tuple
        
        # Create a simple dialog to select merge target
        from PyQt5.QtWidgets import QInputDialog
        
        merge_target, ok = QInputDialog.getItem(
            self,
            "Select Merge Target",
            f"Select which category to merge '{category_to_remove}' expenses into:",
            available_categories,
            0,  # Default to first item
            False  # Not editable
        )
        # Apply dark theme to the input dialog
        if hasattr(self, 'window') and self.window():
            input_dialog = self.findChild(QInputDialog)
            if input_dialog:
                input_dialog.setStyleSheet("""
                    QDialog {
                        background-color: #2d2d2d;
                        color: #e0e0e0;
                    }
                    QComboBox {
                        background-color: #252526;
                        color: #e0e0e0;
                        border: 1px solid #404040;
                        border-radius: 4px;
                        padding: 6px;
                        font-family: "Segoe UI";
                    }
                    QComboBox QAbstractItemView {
                        background-color: #252526;
                        color: #e0e0e0;
                        border: 1px solid #404040;
                        selection-background-color: #007acc;
                    }
                    QLabel {
                        color: #e0e0e0;
                        font-family: "Segoe UI";
                    }
                    QPushButton {
                        background-color: #007acc;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: 500;
                        font-family: "Segoe UI";
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                """)
        
        if ok:
            return merge_target  # ✅ Return string only
        else:
            return None  # User cancelled

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
        self.resize(420, 420)

        layout = QVBoxLayout(self)

        self.category_dropdown = QComboBox()
        self.category_dropdown.setMinimumHeight(35)
        self.category_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.category_dropdown.addItems(categories)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.amount_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setSelectedDate(QDate.currentDate())
        self.calendar_widget.setDateTextFormat(QDate.currentDate(), 
                                             self.get_highlighted_date_format())

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Enter description")
        self.desc_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_dropdown)
        category_hint = QLabel("💡 Need a new category? Use the '📁 Categories' button in the main toolbar")
        category_hint.setStyleSheet("""
            QLabel {
                color: #ffb86c;
                background-color: #443322;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ffa500;
                font-size: 11px;
            }
        """)
        category_hint.setWordWrap(True)
        layout.addWidget(category_hint)
        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(self.amount_input)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.calendar_widget)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.desc_input)
        layout.addWidget(button_box)

        

    def get_highlighted_date_format(self):
        """Return formatting for highlighted current date"""
        format = QTextCharFormat()
        format.setBackground(QColor("#007acc"))  # Blue background
        format.setForeground(QColor("#ffffff"))  # White text
        format.setFontWeight(QFont.Bold)
        return format

    def get_data(self):
        try:
            return {
                "category": self.category_dropdown.currentText(),
                "amount": float(self.amount_input.text()),
                "date": self.calendar_widget.selectedDate().toString("yyyy-MM-dd"),
                "description": self.desc_input.text(),
            }
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
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
