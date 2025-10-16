import csv
import logging
import os
import sys
from datetime import datetime

import openpyxl
import pandas as pd
from fpdf import FPDF
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QComboBox, QDateEdit, QFileDialog,
                             QHBoxLayout, QHeaderView, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QTabWidget, QVBoxLayout,
                             QWidget, QAction)

from expense_tracker_app.data_manager import DataManager
from expense_tracker_app.dialogs import AddExpenseDialog, CategoryDialog
from expense_tracker_app.import_service import DataImportService
from expense_tracker_app.reports import ReportService
from expense_tracker_app.widgets import DashboardWidget, ExpenseTracker

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("expense_tracker.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# Quiet down noisy libraries
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.debug("Application started with logging configured")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.setWindowTitle("Expense Tracker")

        # Set a proper default window size
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)

        # Only initialize UI if not in test mode
        if (
            not hasattr(self.data_manager, "__class__")
            or self.data_manager.__class__.__name__ != "Mock"
        ):
            # AUTO-MIGRATE CATEGORIES ON STARTUP
            self.migrate_categories_on_startup()

            # Apply dark theme to the main window
            self.setStyleSheet(
                """
                QMainWindow {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1a1a2e, stop:1 #16213e);
                    color: #e2e2e2;
                }
            """
            )

            # Tabs widget as central
            self.tabs = QTabWidget()
            self.setCentralWidget(self.tabs)

            # Expenses Tab
            self.expenses_tab = QWidget()
            expenses_layout = QVBoxLayout(self.expenses_tab)
            self.data_manager = DataManager()

            self.expense_tracker = ExpenseTracker(self.data_manager)
            expenses_layout.addWidget(self.expense_tracker)
            self.tabs.addTab(self.expenses_tab, "Expenses")

            # Dashboard Tab
            self.dashboard_tab = QWidget()
            dash_layout = QVBoxLayout(self.dashboard_tab)
            self.dashboard = DashboardWidget(self.data_manager)
            dash_layout.addWidget(self.dashboard)
            self.tabs.addTab(self.dashboard_tab, "Dashboard")

            # Reports Tab
            self.setup_reports_tab()

            # Menu bar
            self.create_menus()

            # Refresh dashboard on tab switch
            self.tabs.currentChanged.connect(self.refresh_dashboard_on_switch)

    def create_menus(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(
            """
            QMenuBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border-bottom: 1px solid #404040;
            font-family: "Segoe UI";
        }
        QMenuBar::item {
            background: transparent;
            padding: 6px 12px;
        }
        QMenuBar::item:selected {
            background-color: #007acc;
            border-radius: 2px;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #404040;
        }
        QMenu::item {
            padding: 6px 24px 6px 16px;
        }
        QMenu::item:selected {
            background-color: #007acc;
        }
    """
        )

        # ---- File Menu ----
        file_menu = menubar.addMenu("File")

        # Import submenu
        import_menu = file_menu.addMenu("Import")
        import_csv_action = import_menu.addAction("Import CSV")
        import_csv_action.triggered.connect(self.import_from_csv)
        import_excel_action = import_menu.addAction("Import Excel")
        import_excel_action.triggered.connect(self.import_from_excel)

        # Export submenu
        export_menu = file_menu.addMenu("Export")
        export_excel_csv_action = export_menu.addAction("Export to Excel/CSV")
        export_excel_csv_action.triggered.connect(self.export_to_excel_or_csv)
        export_pdf_action = export_menu.addAction("Export to PDF")
        export_pdf_action.triggered.connect(self.export_to_pdf)

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)

        # ---- Tools Menu ----
        tools_menu = menubar.addMenu("Tools")  # Add a Tools menu

        # Categories action
        categories_action = QAction("📁 Categories", self)
        categories_action.triggered.connect(self.open_category_dialog)  # Connect to your category dialog
        tools_menu.addAction(categories_action)

        # Add category cleanup tool
        cleanup_action = QAction("🔄 Cleanup Categories", self)
        cleanup_action.triggered.connect(self.cleanup_categories)
        tools_menu.addAction(cleanup_action)

        # ---- Budget Menu
        budget_menu = menubar.addMenu("💰 Budget")

        budget_action = QAction("Set Budgets", self)
        budget_action.setShortcut("Ctrl+B")
        budget_action.triggered.connect(self.open_budget_dialog)
        budget_menu.addAction(budget_action)

        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction(
            "Show Expenses", lambda: self.tabs.setCurrentWidget(self.expenses_tab)
        )
        view_menu.addAction(
            "Show Dashboard", lambda: self.tabs.setCurrentWidget(self.dashboard_tab)
        )
        view_menu.addAction(
            "Show Reports", lambda: self.tabs.setCurrentWidget(self.reports_tab)
        )

        # Help
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")

    def setup_reports_tab(self):
        self.reports_tab = QWidget()
        reports_layout = QVBoxLayout(self.reports_tab)

        title = QLabel("Reports & Exports")
        title.setStyleSheet(
            """
            QLabel {
                color: #00ffff;
                font-family: "Segoe UI";
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f3460, stop:0.5 #533483, stop:1 #e94560);
                border-radius: 8px;
                margin: 5px;
            }
        """
        )
        reports_layout.addWidget(title)

        filter_layout = QHBoxLayout()

        # Get dynamic date range from data
        all_dates = self.get_all_expense_dates()
        if all_dates:
            sorted_dates = sorted(all_dates)
            start_date = QDate.fromString(sorted_dates[0], "yyyy-MM-dd")
            end_date = QDate.fromString(sorted_dates[-1], "yyyy-MM-dd")
        else:
            # Fallback if no data
            start_date = QDate.currentDate().addMonths(-1)
            end_date = QDate.currentDate()

        filter_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(start_date)  # Use dynamic start date
        self.start_date.setStyleSheet(
            """
            QDateEdit {
                background: #2d2d2d;
                color: white;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                font-family: "Segoe UI";
                min-width: 100px;
            }
        """
        )
        calendar = self.start_date.calendarWidget()
        if calendar:
            calendar.setDateTextFormat(QDate.currentDate(), self.get_highlighted_date_format())

        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("To:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(end_date)  # Use dynamic end date
        self.end_date.setStyleSheet(self.start_date.styleSheet())
        calendar = self.end_date.calendarWidget()
        if calendar:
            calendar.setDateTextFormat(QDate.currentDate(), self.get_highlighted_date_format())

        filter_layout.addWidget(self.end_date)

        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All")
        self.category_filter.addItems(
            self.expense_tracker.data_manager.get_all_categories()
        )
        self.category_filter.setStyleSheet(
            """
            QComboBox {
                background: #2d2d2d;
                color: white;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
                font-family: "Segoe UI";
                min-width: 120px;
            }
        """
        )
        filter_layout.addWidget(self.category_filter)

        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.setStyleSheet(
            """
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
        """
        )
        apply_filter_btn.clicked.connect(self.update_report_view)
        filter_layout.addWidget(apply_filter_btn)

        reports_layout.addLayout(filter_layout)

        self.summary_label = QLabel("Summary: No data")
        self.summary_label.setStyleSheet(
            """
            QLabel {
                color: #ffff00;
                font-family: "Segoe UI";
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
                background: #1a1a2e;
                border: 1px solid #ffff00;
                border-radius: 6px;
                margin: 5px;
            }
        """
        )
        reports_layout.addWidget(self.summary_label)

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(
            ["Category", "Amount", "Date", "Description"]
        )
        self.report_table.horizontalHeader().setStretchLastSection(True)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Dark neon table styling
        self.report_table.setStyleSheet(
            """
            QTableWidget {
            background-color: #252526;
            color: #e0e0e0;
            gridline-color: #404040;
            border: 1px solid #404040;
            border-radius: 4px;
            font-family: "Segoe UI";
            font-size: 12px;
        }
        
        QTableWidget::item {
            background-color: #252526;
            color: #e0e0e0;
            padding: 8px 12px;
            border-bottom: 1px solid #404040;
        }
        
        QTableWidget::item:selected {
            background-color: #007acc;
            color: #ffffff;
        }
        
        QHeaderView::section {
            background-color: #333333;
            color: #ffffff;
            padding: 10px;
            border: none;
            border-right: 1px solid #404040;
            border-bottom: 2px solid #007acc;
            font-weight: 600;
            font-family: "Segoe UI";
            font-size: 12px;
        }
    """
        )

        self.report_table.setShowGrid(True)
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setAlternatingRowColors(False)

        reports_layout.addWidget(self.report_table)

        btn_layout = QHBoxLayout()

        btn_excel_csv = QPushButton("Export to Excel/CSV")
        btn_pdf = QPushButton("Export to PDF")

        # Professional button styling
        button_style = """
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px 20px;
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
        """

        btn_excel_csv.setStyleSheet(button_style)
        btn_pdf.setStyleSheet(button_style)

        btn_excel_csv.clicked.connect(self.export_to_excel_or_csv)
        btn_pdf.clicked.connect(self.export_to_pdf)
        btn_layout.addWidget(btn_excel_csv)
        btn_layout.addWidget(btn_pdf)
        reports_layout.addLayout(btn_layout)

        reports_layout.addStretch()
        self.tabs.addTab(self.reports_tab, "Reports")

    def get_highlighted_date_format(self):
        """Return formatting for highlighted current date"""
        from PyQt5.QtGui import QTextCharFormat, QColor, QFont
        from PyQt5.QtCore import QDate
        
        format = QTextCharFormat()
        format.setBackground(QColor("#007acc"))  # Blue background
        format.setForeground(QColor("#ffffff"))  # White text
        format.setFontWeight(QFont.Bold)
        return format

    def migrate_categories_on_startup(self):
        """Automatically migrate categories to proper case on application startup"""
        try:
            # First, migrate all categories to proper capitalization
            migrated_count = self.data_manager.migrate_categories_to_proper_case()
            
            # Then, auto-merge any remaining duplicates
            merged_count = self.data_manager.auto_merge_duplicate_categories()
            
            if migrated_count > 0 or merged_count > 0:
                logger.info(f"🔄 Migrated {migrated_count} categories and merged {merged_count} duplicates")
                
                # Show a one-time notification to user
                QMessageBox.information(
                    self,
                    "Categories Updated",
                    f"Your categories have been automatically organized:\n\n"
                    f"• {migrated_count} categories capitalized\n"
                    f"• {merged_count} duplicate groups merged\n\n"
                    f"All expenses are now properly categorized with consistent naming."
                )
        except Exception as e:
            logger.error(f"Error during category migration: {e}")

    def cleanup_categories(self):
        """Manual category cleanup tool"""
        try:
            # Run the auto-merge function
            merged_count = self.data_manager.auto_merge_duplicate_categories()
            
            if merged_count > 0:
                QMessageBox.information(
                    self,
                    "Categories Cleaned Up",
                    f"Successfully merged {merged_count} groups of duplicate categories.\n\n"
                    f"All your expenses are now organized with consistent category names."
                )
            else:
                QMessageBox.information(
                    self,
                    "No Changes Needed",
                    "Your categories are already properly organized with no duplicates found."
                )
                
            # Refresh the UI
            self.refresh_all_components()
            
        except Exception as e:
            logger.error(f"Error during category cleanup: {e}")
            QMessageBox.warning(
                self,
                "Cleanup Failed",
                f"Could not cleanup categories: {str(e)}"
            )

    def update_report_view(self):
        """Update the report table with currently filtered expenses."""
        filtered = self.get_filtered_expenses()
        self.report_table.setRowCount(0)

        total_amount = 0
        categories = set()

        for row_idx, exp in enumerate(filtered):
            self.report_table.insertRow(row_idx)

            values = [
                exp.get("category", ""),
                str(exp.get("amount", "")),
                exp.get("date", ""),
                exp.get("description", ""),
            ]

            # accumulate
            try:
                amt_val = float(exp.get("amount", 0))
                total_amount += amt_val
            except Exception:
                pass
            categories.add(exp.get("category", ""))

            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                self.report_table.setItem(row_idx, col_idx, item)

        self.report_table.resizeColumnsToContents()

        if filtered:
            cats = ", ".join(sorted(categories))
            self.summary_label.setText(
                f"Summary: {len(filtered)} expenses | Categories: {cats} | Total: ₱{total_amount:.2f}"
            )
        else:
            self.summary_label.setText("Summary: No data")

    def refresh_dashboard_on_switch(self, index):
        if self.tabs.widget(index) == self.dashboard_tab:
            logger.debug("Dashboard tab selected, updating dashboard")
            self.dashboard.update_dashboard()

    def get_filtered_expenses(self):
        """Return filtered expenses based on category and date range."""
        try:
            self.data_manager.load_expense()
        except TypeError:
            pass

        expenses = []
        category_filter = self.category_filter.currentText().strip().lower()

        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        for cat, items in self.data_manager.expenses.items():
            for e in items:
                entry_category = (
                    e.get("category")
                    if isinstance(e, dict) and e.get("category")
                    else cat
                )
                if entry_category is None:
                    entry_category = "Uncategorized"

                exp_date = None
                try:
                    exp_date = datetime.strptime(e.get("date", ""), "%Y-%m-%d").date()
                except Exception:
                    exp_date = None

                match_category = (category_filter == "all") or (
                    str(entry_category).strip().lower() == category_filter
                )

                match_date = not exp_date or (start <= exp_date <= end)

                if match_category and match_date:
                    expenses.append(
                        {
                            "category": entry_category,
                            "amount": e.get("amount", 0),
                            "date": e.get("date", ""),
                            "description": e.get("description", ""),
                        }
                    )

        return expenses

    def get_all_expense_dates(self):
        """Get all unique dates from expenses for dynamic date range"""
        all_dates = []
        for category, expenses in self.data_manager.expenses.items():
            for expense in expenses:
                date_str = expense.get("date", "")
                if date_str:
                    try:
                        # Validate the date format
                        datetime.strptime(date_str, "%Y-%m-%d")
                        all_dates.append(date_str)
                    except ValueError:
                        continue  # Skip invalid dates
        return all_dates

    def update_report_date_ranges(self):
        """Update the report date ranges when new data is loaded"""
        all_dates = self.get_all_expense_dates()
        if all_dates:
            sorted_dates = sorted(all_dates)
            start_date = QDate.fromString(sorted_dates[0], "yyyy-MM-dd")
            end_date = QDate.fromString(sorted_dates[-1], "yyyy-MM-dd")

            # Update the date widgets
            self.start_date.setDate(start_date)
            self.end_date.setDate(end_date)

    def update_dashboard(self):
        """Update dashboard with latest data."""
        if hasattr(self, 'dashboard'):
            self.dashboard.update_dashboard()
            # Add budget alerts update
            if hasattr(self.dashboard, 'update_budget_alerts'):
                self.dashboard.update_budget_alerts()

    def export_to_excel_or_csv(self, filepath=None, filetype=None):
        """Export to Excel or CSV. If filepath provided, extension determines format."""
        logger.info("Starting Excel/CSV export (MainWindow) -> %s", filepath)
        data = self.get_filtered_expenses()
        if not data:
            logger.info("No expenses to export (Excel/CSV)")
            if filepath:
                if filepath.lower().endswith(".csv"):
                    ReportService.export_to_csv({}, filepath)
                else:
                    ReportService.export_to_excel({}, filepath)
                return True
            QMessageBox.information(self, "Export", "No expenses to export.")
            return False

        try:
            if filepath:
                if filepath.lower().endswith(".csv"):
                    ReportService.export_to_csv(data, filepath)
                else:
                    ReportService.export_to_excel(data, filepath)
                logger.info("Exported file to %s", filepath)
                return True
            else:
                file_path, selected_filter = QFileDialog.getSaveFileName(
                    self,
                    "Save File",
                    "expenses.xlsx",
                    "Excel Files (*.xlsx);;CSV Files (*.csv)",
                )
                if file_path:
                    if selected_filter.startswith(
                        "Excel"
                    ) or file_path.lower().endswith(".xlsx"):
                        if not file_path.lower().endswith(".xlsx"):
                            file_path += ".xlsx"
                        ReportService.export_to_excel(data, file_path)
                    else:
                        if not file_path.lower().endswith(".csv"):
                            file_path += ".csv"
                        ReportService.export_to_csv(data, file_path)
                    QMessageBox.information(self, "Export", f"Exported to {file_path}")
                    return True
        except Exception as e:
            logger.exception("Excel/CSV export failed (MainWindow): %s", e)
            QMessageBox.warning(self, "Export Error", str(e))
        return False

    def export_to_pdf(self, filepath=None):
        """Export to PDF. If filepath provided, export directly (used by tests)."""
        logger.info("Starting PDF export (MainWindow) -> %s", filepath)
        data = self.get_filtered_expenses()
        if not data:
            logger.info("No expenses to export (PDF)")
            if filepath:
                ReportService.export_to_pdf({}, filepath)
                return True
            QMessageBox.information(self, "Export", "No expenses to export.")
            return False

        try:
            if filepath:
                ReportService.export_to_pdf(data, filepath)
                logger.info("Exported PDF to %s", filepath)
                return True
            else:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Save PDF File", "expenses.pdf", "PDF Files (*.pdf)"
                )
                if file_path:
                    ReportService.export_to_pdf(data, file_path)
                    QMessageBox.information(self, "Export", f"Exported to {file_path}")
                    return True
        except Exception as e:
            logger.exception("PDF export failed (MainWindow): %s", e)
            QMessageBox.warning(self, "Export Error", str(e))
        return False

    def import_from_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Import from CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if file_name:
            try:
                DataImportService.import_from_csv(file_name, self.data_manager)
                self.data_manager.load_expense()

                # AUTO-REFRESH ALL COMPONENTS
                self.refresh_all_components()

                QMessageBox.information(
                    self,
                    "Import Successful",
                    "Expenses imported successfully!\n\nAll views have been refreshed.",
                )
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"Error: {e}")

    def import_from_excel(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Import from Excel", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_name:
            try:
                DataImportService.import_from_excel(file_name, self.data_manager)
                self.data_manager.load_expense()

                # AUTO-REFRESH ALL COMPONENTS
                self.refresh_all_components()

                QMessageBox.information(
                    self,
                    "Import Successful",
                    "Expenses imported successfully!\n\nAll views have been refreshed.",
                )
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"Error: {e}")

    def refresh_all_components(self):
        """Refresh all components after data changes"""
        # Refresh expense tracker
        self.expense_tracker.show_expense()

        # Refresh dashboard
        self.dashboard.update_dashboard()

        # Refresh reports tab
        self.update_report_view()

        # Refresh category dropdowns
        self.expense_tracker.refresh_category_dropdowns()

        # Update date ranges for charts and reports
        self.update_report_date_ranges()

        logger.debug("All components refreshed after data import")

    def open_budget_dialog(self):
        """Open budget management dialog from main menu."""
        try:
            from expense_tracker_app.widgets import BudgetDialog
            dialog = BudgetDialog(self.data_manager, self)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening budget dialog: {e}")
            QMessageBox.warning(self, "Error", "Could not open budget dialog.")

    def open_category_dialog(self):
        """Open category management dialog."""
        try:
            # If you have a category dialog in widgets.py, import and use it
            from expense_tracker_app.dialogs import CategoryDialog
            # This will open the category dialog from your expense tracker
            dialog = CategoryDialog(self.data_manager, self)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Error opening category dialog: {e}")
            QMessageBox.warning(self, "Error", "Could not open category dialog.")

    def exit_application(self):
        """Exit the application with save confirmation - matches dashboard exit behavior"""

        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to save and exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Save data
            self.data_manager.save_data()

            # Show confirmation message
            QMessageBox.information(
                self,
                "Save Successful",
                "Thank you for using Expense Tracker.\nYour data has been saved successfully.",
            )

            # Close the application
            QApplication.quit()
        # If No is selected, do nothing (stay in the application)

    def closeEvent(self, event):
        """Handle window close (X button) - same behavior as exit menu"""

        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to save and exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.data_manager.save_data()
            # Don't show the success message here to avoid multiple dialogs
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Professional Dark Theme
    app.setStyleSheet(
        """
        QMainWindow {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        
        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #2d2d2d;
            border-radius: 4px;
            margin: 4px;
        }
        
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #e0e0e0;
            padding: 10px 16px;
            margin: 2px;
            border-radius: 4px;
            font-family: "Segoe UI";
            font-weight: 500;
            font-size: 12px;
            border: none;
            min-width: 80px;
        }
        
        QTabBar::tab:selected {
            background-color: #007acc;
            color: #ffffff;
            font-weight: 600;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #4a4a4a;
        }
        
        QMessageBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #404040;
            border-radius: 6px;
        }
        
        QMessageBox QLabel {
            color: #e0e0e0;
            font-family: "Segoe UI";
            font-size: 13px;
        }
        
        QMessageBox QPushButton {
            background-color: #007acc;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
            font-family: "Segoe UI";
            font-size: 12px;
            min-width: 80px;
        }
        
        QMessageBox QPushButton:hover {
            background-color: #005a9e;
        }
        
        QMessageBox QPushButton:pressed {
            background-color: #004578;
        }
        QDialog {
        background-color: #2d2d2d;
        color: #e0e0e0;
        }
        QInputDialog {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QMessageBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QListWidget {
            background-color: #252526;
            color: #e0e0e0;
            border: 1px solid #404040;
        }
        QLineEdit {
            background-color: #252526;
            color: #e0e0e0;
            border: 1px solid #404040;
        }
        QComboBox {
            background-color: #252526;
            color: #e0e0e0;
            border: 1px solid #404040;
        }
        QLabel {
            color: #e0e0e0;
        }
        
    """
    )

    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
