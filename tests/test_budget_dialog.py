import pytest
from PyQt5.QtWidgets import QApplication, QDialogButtonBox
from PyQt5.QtCore import Qt
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
        assert dialog.budget_manager == data_manager.budget_manager
        assert dialog.isVisible() is False

    def test_category_dropdown_population(self, app, data_manager):
        """Test that category dropdown is populated with existing categories"""
        # Add some categories to data manager
        data_manager.add_category("Food")
        data_manager.add_category("Transport")
        
        dialog = BudgetDialog(data_manager)
        dialog.show()  # Trigger population
        
        # Check that categories are in the dropdown
        # This is a basic test - actual UI interaction would be more complex
        assert dialog.category_combo.count() >= 2  # Should have at least our categories

    def test_set_budget_through_dialog(self, app, data_manager):
        """Test setting budget through dialog interface"""
        dialog = BudgetDialog(data_manager)
        
        # This would simulate UI interactions in a real test
        # For now, test the underlying method
        success = dialog.set_budget("Food", 500.0)
        assert success is True
        assert data_manager.budget_manager.budgets.get("food") == 500.0

    def test_remove_budget_through_dialog(self, app, data_manager):
        """Test removing budget through dialog interface"""
        dialog = BudgetDialog(data_manager)
        
        # First set a budget
        data_manager.budget_manager.set_budget("Food", 500.0)
        assert "food" in data_manager.budget_manager.budgets
        
        # Then remove it
        success = dialog.remove_budget("Food")
        assert success is True
        assert "food" not in data_manager.budget_manager.budgets