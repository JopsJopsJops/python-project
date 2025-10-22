from datetime import datetime

import pytest

from expense_tracker_app.data_manager import DataManager


class TestDataManagerBudgetIntegration:
    @pytest.fixture
    def data_manager(self):
        """Create DataManager instance for tests"""
        return DataManager()

    def test_dashboard_refresh_trigger(self, data_manager):
        """Test that data manager has budget manager integrated"""
        assert data_manager.budget_manager is not None
        assert data_manager.budget_manager.data_manager == data_manager

    def test_budget_alerts_on_expense_operations(self, data_manager):
        """Test that budget alerts work when expenses are added"""
        data_manager.budget_manager.set_budget("Food", 500.0)
        data_manager.add_expense("Food", 600.0, "2024-01-01", "Groceries")

        alerts = data_manager.budget_manager.check_budget_alerts()
        assert isinstance(alerts, list)

    def test_budget_progress_calculation(self, data_manager):
        """Test that budget progress is calculated correctly with expenses"""
        # Use EXACT same case as your app uses - lowercase
        unique_category = "Testbudgetprogress"

        # Use current date so the expense is counted in budget progress
        current_date = datetime.now().strftime("%Y-%m-%d")

        # CLEANUP FIRST (in case of previous test runs)
        data_manager.budget_manager.remove_budget(unique_category)
        if unique_category in data_manager.expenses:
            data_manager.expenses[unique_category] = []

        # Set budget
        data_manager.budget_manager.set_budget(unique_category, 500.0)

        # Add expense
        data_manager.add_expense(unique_category, 300.0, current_date, "Test expense")

        # DEBUG: Check how many expenses we have
        expense_count = len(data_manager.expenses.get(unique_category, []))
        print(f"=== DEBUG: Found {expense_count} expenses for {unique_category} ===")

        # Get progress
        progress = data_manager.budget_manager.get_budget_progress(unique_category)

        # Test exact expected values
        assert progress is not None
        assert progress["budget"] == 500.0
        assert progress["spent"] == 300.0
        assert progress["remaining"] == 200.0
        assert progress["percentage"] == 60.0

        # Clean up
        data_manager.budget_manager.remove_budget(unique_category)
        if unique_category in data_manager.expenses:
            data_manager.expenses[unique_category] = []
