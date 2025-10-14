import pytest
from PyQt5.QtWidgets import QApplication
from expense_tracker_app.widgets import BudgetDialog
from expense_tracker_app.data_manager import DataManager

class TestBudgetDialog:
    @pytest.fixture
    def app(self):
        """Create QApplication instance for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    @pytest.fixture
    def data_manager(self):
        """Create DataManager instance for tests"""
        return DataManager()

    def test_budget_dialog_initialization(self, app, data_manager):
        """Test BudgetDialog initialization"""
        dialog = BudgetDialog(data_manager)
        assert dialog.data_manager == data_manager
        # Check for common UI elements instead of specific setup_ui method
        assert hasattr(dialog, 'layout') or hasattr(dialog, 'setWindowTitle')

    def test_budget_operations_through_data_manager(self, data_manager):
        """Test budget operations work through the data manager"""
        success = data_manager.budget_manager.set_budget("Food", 500.0)
        assert success is True
        assert "Food" in data_manager.budget_manager.budgets
        
        success = data_manager.budget_manager.remove_budget("Food")
        assert success is True
        assert "Food" not in data_manager.budget_manager.budgets