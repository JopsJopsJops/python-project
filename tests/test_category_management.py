import pytest
import os
from unittest import mock
from expense_tracker_app.data_manager import DataManager


class TestCategoryManagement:
    """Test category management functionality without GUI dependencies"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup for each test - no QApplication needed"""
        self.dm = DataManager()
        self.dm.expenses = {}
        self.dm.categories = ["Uncategorized"]
        yield
        # Cleanup
        if os.path.exists("test_expenses.json"):
            os.remove("test_expenses.json")

    def test_category_normalization(self):
        """Test that categories are properly capitalized"""
        dm = DataManager()

        assert dm.normalize_category_name("food") == "Food"
        assert dm.normalize_category_name("FAST FOOD") == "Fast Food"
        assert dm.normalize_category_name("work equipment") == "Work Equipment"

    def test_category_duplicate_detection(self):
        """Test that duplicate categories are detected"""
        dm = DataManager()

        success, message = dm.add_category("Food")
        assert success is True

        # Try to add duplicate with different case
        success, message = dm.add_category("food")
        assert success is False
        assert "already exists" in message.lower()

    def test_remove_category_with_merge(self):
        """Test removing category with merge functionality"""
        dm = self.dm

        # Add categories and expenses
        dm.add_category("Food")
        dm.add_category("Dining")
        dm.add_expense("Food", 100, "2024-01-01", "Lunch")

        # Mock the confirmation dialog
        with mock.patch("PyQt5.QtWidgets.QMessageBox.question") as mock_question:
            mock_question.return_value = mock.MagicMock(Yes=16384)
            success, message = dm.remove_category("Food", "Dining")

        assert success is True
        assert "Food" not in dm.expenses
        assert "Dining" in dm.expenses
        assert len(dm.expenses["Dining"]) == 1

    def test_remove_category_merge_flow(self):
        """Test removing a category - simplified version"""
        dm = DataManager()
        dm.expenses.clear()
        dm.categories.clear()

        # Setup test data
        dm.categories = ["Food", "Dining"]
        dm.add_expense("Food", 100, "2024-01-01", "Lunch")

        # Mock the confirmation dialog
        with mock.patch("PyQt5.QtWidgets.QMessageBox.question") as mock_question:
            mock_question.return_value = 16384  # QMessageBox.Yes value
            result = dm.remove_category("Food")

        assert "Food" not in dm.categories
        assert "Food" not in dm.expenses

        all_expenses = dm.list_all_expenses()
        assert len(all_expenses) == 1
        assert all_expenses[0]["amount"] == 100
        assert result is True or (isinstance(result, tuple) and result[0] is True)

    def test_remove_category_uncategorized_confirmation(self):
        """Test that removing 'Uncategorized' category works"""
        dm = DataManager()
        dm.categories.clear()
        dm.categories.extend(["Food", "Transport", "Uncategorized"])
        dm.expenses.clear()

        # Mock any dialogs that might appear
        with mock.patch("PyQt5.QtWidgets.QMessageBox.question") as mock_question:
            mock_question.return_value = 16384  # Yes
            result = dm.remove_category("Uncategorized")

        assert "Food" in dm.categories
        assert "Transport" in dm.categories

        if isinstance(result, tuple):
            assert result[0] is True
        else:
            assert result is True

    def test_remove_empty_category(self):
        """Test removing category with no expenses"""
        dm = DataManager()
        dm.add_category("Test")

        success, message = dm.remove_category("Test")
        assert success is True
        assert "Test" not in dm.categories

    def test_remove_nonexistent_category(self):
        """Test removing category that doesn't exist"""
        dm = DataManager()

        success, message = dm.remove_category("Nonexistent")
        assert success is False
        assert "not found" in message.lower()

    def test_merge_target_normalization(self):
        """Test that merge targets are also normalized"""
        dm = DataManager()
        dm.add_category("Food")
        dm.add_expense("Food", 100, "2024-01-01", "Lunch")

        # Mock dialogs
        with mock.patch("PyQt5.QtWidgets.QMessageBox.question") as mock_question:
            mock_question.return_value = 16384
            success, message = dm.remove_category("Food", "food")

        assert success is True
