# test_data_manager.py
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from expense_tracker_app.data_manager import DataManager


class TestDataManager:
    @pytest.mark.unit
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.data_manager = DataManager(file_path=self.temp_file.name)

    @pytest.mark.unit
    def teardown_method(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    @pytest.mark.unit
    def test_init_default_filename(self):
        """Test initialization with default filename."""
        dm = DataManager()
        assert dm.filename == "expenses.json"
        assert isinstance(dm.expenses, dict)
        # Accept either empty or sample data

    @pytest.mark.unit
    def test_init_custom_file_path(self):
        dm = DataManager(file_path="/custom/path.json")
        assert dm.filename == "/custom/path.json"

    @pytest.mark.unit
    def test_load_expense_file_not_exists(self):
        with patch("os.path.exists", return_value=False):
            self.data_manager.load_expense()
            assert self.data_manager.expenses == {}

    @pytest.mark.unit
    def test_load_expense_success(self):
        test_data = {
            "expenses": {
                "Food": [
                    {
                        "id": 1,
                        "amount": 10.0,
                        "date": "2023-01-01",
                        "description": "Lunch",
                    }
                ]
            },
            "categories": ["Food", "Travel"],
        }
        with open(self.temp_file.name, "w") as f:
            json.dump(test_data, f)

        self.data_manager.load_expense()
        assert "Food" in self.data_manager.expenses
        assert len(self.data_manager.expenses["Food"]) == 1
        assert self.data_manager.categories == ["Food", "Travel"]

    @pytest.mark.unit
    def test_load_expense_json_decode_error(self):
        with open(self.temp_file.name, "w") as f:
            f.write("invalid json")

        with patch("logging.Logger.warning") as mock_warning:
            self.data_manager.load_expense()
            mock_warning.assert_called()

    @pytest.mark.unit
    def test_load_expense_generic_exception(self):
        with patch("builtins.open", side_effect=Exception("Test error")):
            with patch("logging.Logger.error") as mock_error:
                self.data_manager.load_expense()
                mock_error.assert_called()
                assert self.data_manager.expenses == {}

    @pytest.mark.unit
    def test_save_data_success(self):
        self.data_manager.expenses = {
            "Food": [{"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}]
        }
        self.data_manager.categories = ["Food", "Travel"]

        self.data_manager.save_data()

        with open(self.temp_file.name, "r") as f:
            saved_data = json.load(f)

        assert "Food" in saved_data["expenses"]
        assert "Travel" in saved_data["categories"]

    @pytest.mark.unit
    def test_save_data_no_filename(self):
        dm = DataManager(filename="")
        dm.expenses = {"Food": []}
        dm.save_data()  # Should not raise exception

    @pytest.mark.unit
    def test_save_data_directory_creation(self):
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "subdir", "expenses.json")

        try:
            dm = DataManager(file_path=file_path)
            dm.expenses = {"Food": []}
            dm.save_data()

            assert os.path.exists(file_path)
        finally:
            import shutil

            shutil.rmtree(temp_dir)

    @pytest.mark.unit
    def test_save_data_exception(self):
        with patch("builtins.open", side_effect=Exception("Test error")):
            with patch("logging.Logger.error") as mock_error:
                self.data_manager.save_data()
                mock_error.assert_called()

    @pytest.mark.unit
    def test_add_category_new(self):
        initial_count = len(self.data_manager.categories)
        self.data_manager.add_category("Entertainment")

        assert "Entertainment" in self.data_manager.categories
        assert len(self.data_manager.categories) == initial_count + 1

    @pytest.mark.unit
    def test_add_category_existing(self):
        initial_count = len(self.data_manager.categories)
        self.data_manager.add_category("Food")  # Already exists

        assert len(self.data_manager.categories) == initial_count

    @pytest.mark.unit
    def test_add_category_merge(self):
        self.data_manager.expenses = {
            "OldCat": [{"amount": 10.0, "date": "2023-01-01", "description": "Test"}]
        }
        self.data_manager.categories = ["OldCat", "NewCat"]

        self.data_manager.add_category("OldCat", merge_target="NewCat")

        assert "OldCat" not in self.data_manager.categories
        assert "OldCat" not in self.data_manager.expenses
        assert "NewCat" in self.data_manager.expenses
        assert len(self.data_manager.expenses["NewCat"]) == 1

    @pytest.mark.unit
    def test_add_category_merge_invalid(self):
        with pytest.raises(ValueError):
            self.data_manager.add_category(
                "NonExistent", merge_target="AlsoNonExistent"
            )

    @pytest.mark.unit
    def test_remove_category_exists(self):
        self.data_manager.categories = ["Food", "TestCat"]
        self.data_manager.remove_category("TestCat")

        assert "TestCat" not in self.data_manager.categories

    @pytest.mark.unit
    def test_remove_category_not_exists(self):
        initial_categories = self.data_manager.categories.copy()
        self.data_manager.remove_category("NonExistent")

        assert self.data_manager.categories == initial_categories

    @pytest.mark.unit
    def test_add_expense_valid(self):
        self.data_manager.add_expense("Food", 25.50, "2023-01-01", "Dinner")

        assert "Food" in self.data_manager.expenses
        assert len(self.data_manager.expenses["Food"]) == 1
        expense = self.data_manager.expenses["Food"][0]
        assert expense["amount"] == 25.50
        assert expense["date"] == "2023-01-01"
        assert expense["description"] == "Dinner"
        assert "id" in expense

    @pytest.mark.unit
    def test_add_expense_new_category_auto_add(self):
        self.data_manager.add_expense("NewCategory", 15.0, "2023-01-01", "Test")

        assert "NewCategory" in self.data_manager.categories
        assert "NewCategory" in self.data_manager.expenses

    @pytest.mark.unit
    def test_add_expense_invalid_amount(self):
        with pytest.raises(ValueError):
            self.data_manager.add_expense("Food", "invalid", "2023-01-01", "Test")

    @pytest.mark.unit
    def test_add_expense_negative_amount(self):
        with pytest.raises(ValueError):
            self.data_manager.add_expense("Food", -10.0, "2023-01-01", "Test")

    @pytest.mark.unit
    def test_add_expense_invalid_date(self):
        with pytest.raises(ValueError):
            self.data_manager.add_expense("Food", 10.0, "invalid-date", "Test")

    @pytest.mark.unit
    def test_delete_expense_by_index(self):
        self.data_manager.expenses = {
            "Food": [{"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}]
        }

        result = self.data_manager.delete_expense("Food", 0)

        assert result is True
        assert len(self.data_manager.expenses["Food"]) == 0

    @pytest.mark.unit
    def test_delete_expense_by_record(self):
        record = {"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}
        self.data_manager.expenses = {"Food": [record]}

        result = self.data_manager.delete_expense("Food", record)

        assert result is True
        assert len(self.data_manager.expenses["Food"]) == 0

    @pytest.mark.unit
    def test_delete_expense_category_not_exists(self):
        result = self.data_manager.delete_expense("NonExistent", 0)
        assert result is False

    @pytest.mark.unit
    def test_delete_expense_index_out_of_range(self):
        self.data_manager.expenses = {
            "Food": [{"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}]
        }

        result = self.data_manager.delete_expense("Food", 5)  # Invalid index
        assert result is False

    @pytest.mark.unit
    def test_undo_delete_single(self):
        record = {"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}
        self.data_manager.expenses = {"Food": [record]}
        self.data_manager.delete_expense("Food", record)

        result = self.data_manager.undo_delete()

        assert result is True
        assert len(self.data_manager.expenses["Food"]) == 1

    @pytest.mark.unit
    def test_undo_delete_nothing_to_undo(self):
        result = self.data_manager.undo_delete()
        assert result is False

    @pytest.mark.unit
    def test_undo_clear(self):
        original_expenses = {
            "Food": [{"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}]
        }
        self.data_manager.expenses = original_expenses.copy()
        self.data_manager.clear_all()

        result = self.data_manager.undo_clear()

        assert result is True
        assert self.data_manager.expenses == original_expenses

    @pytest.mark.unit
    def test_get_sorted_expenses(self):
        self.data_manager.expenses = {
            "Food": [
                {"amount": 10.0, "date": "2023-01-02", "description": "Lunch"},
                {"amount": 20.0, "date": "2023-01-01", "description": "Breakfast"},
            ]
        }

        sorted_expenses = self.data_manager.get_sorted_expenses()

        dates = [exp["date"] for exp in sorted_expenses["Food"]]
        assert dates == ["2023-01-01", "2023-01-02"]

    @pytest.mark.unit
    def test_get_category_subtotals(self):
        self.data_manager.expenses = {
            "Food": [
                {"amount": 10.0, "date": "2023-01-01", "description": "Lunch"},
                {"amount": 20.0, "date": "2023-01-02", "description": "Dinner"},
            ],
            "Travel": [{"amount": 50.0, "date": "2023-01-03", "description": "Bus"}],
        }

        subtotals = self.data_manager.get_category_subtotals()

        assert subtotals["Food"] == 30.0
        assert subtotals["Travel"] == 50.0

    @pytest.mark.unit
    def test_search_expenses(self):
        self.data_manager.expenses = {
            "Food": [
                {"amount": 10.0, "date": "2023-01-01", "description": "Lunch at cafe"},
                {
                    "amount": 20.0,
                    "date": "2023-01-02",
                    "description": "Dinner restaurant",
                },
            ]
        }

        results = self.data_manager.search_expenses("cafe")

        assert len(results) == 1
        assert results[0][0] == "Food"
        assert "cafe" in results[0][1]["description"].lower()

    @pytest.mark.unit
    def test_search_expenses_no_match(self):
        self.data_manager.expenses = {
            "Food": [{"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}]
        }

        results = self.data_manager.search_expenses("nonexistent")
        assert len(results) == 0

    @pytest.mark.unit
    def test_update_expense_success(self):
        old_record = {"amount": 10.0, "date": "2023-01-01", "description": "Old"}
        self.data_manager.expenses = {"Food": [old_record]}

        new_data = {
            "category": "Travel",
            "amount": 15.0,
            "date": "2023-01-02",
            "description": "New",
        }
        result = self.data_manager.update_expense("Food", old_record, new_data)

        assert result is True
        assert (
            "Food" not in self.data_manager.expenses
            or len(self.data_manager.expenses["Food"]) == 0
        )
        assert "Travel" in self.data_manager.expenses
        assert self.data_manager.expenses["Travel"][0]["amount"] == 15.0

    @pytest.mark.unit
    def test_update_expense_not_found(self):
        result = self.data_manager.update_expense("Food", {"amount": 10.0}, {})
        assert result is False

    @pytest.mark.unit
    def test_get_expenses_for_category(self):
        self.data_manager.expenses = {
            "Food": [{"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}]
        }

        expenses = self.data_manager.get_expenses_for_category("Food")
        assert len(expenses) == 1

    @pytest.mark.unit
    def test_get_expenses_for_nonexistent_category(self):
        expenses = self.data_manager.get_expenses_for_category("NonExistent")
        assert expenses == []

    @pytest.mark.unit
    def test_get_grand_total(self):
        self.data_manager.expenses = {
            "Food": [{"amount": 10.0}, {"amount": 20.0}],
            "Travel": [{"amount": 30.0}],
        }

        total = self.data_manager.get_grand_total()
        assert total == 60.0

    @pytest.mark.unit
    def test_get_monthly_totals(self):
        self.data_manager.expenses = {
            "Food": [
                {"amount": 10.0, "date": "2023-01-01"},
                {"amount": 20.0, "date": "2023-01-15"},
            ],
            "Travel": [{"amount": 30.0, "date": "2023-02-01"}],
        }

        monthly_totals = self.data_manager.get_monthly_totals()

        assert monthly_totals["2023-01"] == 30.0
        assert monthly_totals["2023-02"] == 30.0

    @pytest.mark.unit
    def test_list_all_expenses(self):
        self.data_manager.expenses = {
            "Food": [{"amount": 10.0, "date": "2023-01-01", "description": "Lunch"}],
            "Travel": [{"amount": 20.0, "date": "2023-01-02", "description": "Bus"}],
        }

        all_expenses = self.data_manager.list_all_expenses()

        assert len(all_expenses) == 2
        assert all("category" in exp for exp in all_expenses)

    @pytest.mark.unit
    def test_has_expenses_true(self):
        self.data_manager.expenses = {"Food": [{"amount": 10.0}]}
        assert self.data_manager.has_expenses() is True

    @pytest.mark.unit
    def test_has_expenses_false(self):
        assert self.data_manager.has_expenses() is False

    @pytest.mark.unit
    def test_clear_all(self):
        self.data_manager.expenses = {"Food": [{"amount": 10.0}]}
        self.data_manager.clear_all()

        assert self.data_manager.expenses == {}
        assert self.data_manager.last_cleared is not None

    @pytest.mark.unit
    def test_list_expenses_alias(self):
        # Test that list_expenses is an alias for get_sorted_expenses
        self.data_manager.expenses = {"Food": [{"amount": 10.0}]}
        result1 = self.data_manager.list_expenses()
        result2 = self.data_manager.get_sorted_expenses()

        assert result1 == result2

    @pytest.mark.unit
    def test_get_all_expenses_alias(self):
        # Test that get_all_expenses is an alias for list_all_expenses
        self.data_manager.expenses = {"Food": [{"amount": 10.0}]}
        result1 = self.data_manager.get_all_expenses()
        result2 = self.data_manager.list_all_expenses()

        assert result1 == result2

    @pytest.mark.unit
    def test_budget_manager_integration(self):
        """Test that DataManager has budget manager integration."""
        dm = DataManager()
        assert hasattr(dm, 'budget_manager')
        assert dm.budget_manager.data_manager == dm
