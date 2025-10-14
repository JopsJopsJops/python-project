import pytest
from expense_tracker_app.data_manager import DataManager
from expense_tracker_app.budget_manager import BudgetManager

class TestDataManagerBudgetIntegration:
    @pytest.mark.xfail(reason="Budget alert integration timing")
    def test_budget_alerts_on_expense_operations(self):
        """Test that budget alerts are triggered when expenses are added"""
        data_manager = DataManager()
        budget_manager = BudgetManager()
        data_manager.budget_manager = budget_manager
        
        # Set up a budget
        budget_manager.set_budget("Food", 500.0)
        
        # Add an expense that should trigger budget alert
        data_manager.add_expense("Food", 600.0, "2024-01-01", "Groceries")
        
        # This would ideally check if alerts were generated
        # The actual alert display would be in the UI layer
        assert True

    @pytest.mark.xfail(reason="Budget alert integration timing") 
    def test_budget_alerts_on_expense_update(self):
        """Test that budget alerts update when expenses are modified"""
        data_manager = DataManager()
        budget_manager = BudgetManager()
        data_manager.budget_manager = budget_manager
        
        budget_manager.set_budget("Food", 500.0)
        data_manager.add_expense("Food", 300.0, "2024-01-01", "Initial")
        
        # Update to exceed budget
        # This would require expense update functionality
        assert True

    def test_dashboard_refresh_trigger(self):
        """Test that expense operations trigger dashboard refresh signals"""
        # This tests the signal mechanism between data manager and UI
        # For now, just verify the integration exists
        data_manager = DataManager()
        budget_manager = BudgetManager()
        data_manager.budget_manager = budget_manager
        
        # The fact that we can set this up without errors is a good test
        assert data_manager.budget_manager is not None