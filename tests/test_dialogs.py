# test_dialogs.py
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QMessageBox

from expense_tracker_app.dialogs import AddExpenseDialog, CategoryDialog

# Setup Qt application for testing


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestCategoryDialog:
    @pytest.mark.gui
    def test_init_with_data_manager(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food", "Travel"]

        dialog = CategoryDialog(mock_dm)

        assert dialog.list_widget.count() == 2
        assert dialog.list_widget.item(0).text() == "Food"

    @pytest.mark.gui
    def test_init_with_list(self, qapp):
        categories = ["Food", "Travel"]
        dialog = CategoryDialog(categories)

        assert dialog.list_widget.count() == 2
        assert dialog.data_manager == categories

    @pytest.mark.gui
    def test_add_category_new(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food"]  # Use real list, not Mock
        mock_dm.save_data = Mock()

        dialog = CategoryDialog(mock_dm)

        with patch(
            "expense_tracker_app.dialogs.QInputDialog.getText",
            return_value=("Travel", True),
        ):
            dialog.add_category()

            # Check if category was added
            assert "Travel" in mock_dm.categories
            mock_dm.save_data.assert_called_once()

    @pytest.mark.gui
    def test_add_category_duplicate(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food"]

        dialog = CategoryDialog(mock_dm)

        with patch("PyQt5.QtWidgets.QInputDialog.getText", return_value=("Food", True)):
            with patch("PyQt5.QtWidgets.QMessageBox.warning") as mock_warning:
                dialog.add_category()
                mock_warning.assert_called_once()

    @pytest.mark.gui
    def test_add_category_cancelled(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food"]

        dialog = CategoryDialog(mock_dm)

        with patch("PyQt5.QtWidgets.QInputDialog.getText", return_value=("", False)):
            initial_categories = mock_dm.categories.copy()
            dialog.add_category()

            # Should not add anything
            assert mock_dm.categories == initial_categories

    @pytest.mark.gui
    def test_remove_category_success(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food", "Travel", "Uncategorized"]
        mock_dm.expenses = {"Travel": [{"amount": 10.0}]}
        mock_dm.save_data = Mock()

        dialog = CategoryDialog(mock_dm)
        dialog.list_widget.addItems(["Food", "Travel", "Uncategorized"])
        dialog.list_widget.setCurrentRow(1)  # Select "Travel"

        with patch(
            "expense_tracker_app.dialogs.QMessageBox.question",
            return_value=QMessageBox.Yes,
        ):
            dialog.remove_category()

            # Check if category was removed
            assert "Travel" not in mock_dm.categories
            mock_dm.save_data.assert_called_once()

    @pytest.mark.gui
    def test_remove_category_uncategorized(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food", "Uncategorized"]

        dialog = CategoryDialog(mock_dm)
        dialog.list_widget.addItems(["Food", "Uncategorized"])
        dialog.list_widget.setCurrentRow(1)  # Select "Uncategorized"

        with patch("PyQt5.QtWidgets.QMessageBox.warning") as mock_warning:
            dialog.remove_category()
            mock_warning.assert_called_once()

    @pytest.mark.gui
    def test_remove_category_no_selection(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food"]

        dialog = CategoryDialog(mock_dm)

        with patch("PyQt5.QtWidgets.QMessageBox.warning") as mock_warning:
            dialog.remove_category()
            mock_warning.assert_called_once()

    @pytest.mark.gui
    def test_remove_category_cancelled(self, qapp):
        mock_dm = Mock()
        mock_dm.categories = ["Food", "Travel"]
        mock_dm.expenses = {}

        dialog = CategoryDialog(mock_dm)
        dialog.list_widget.addItems(["Food", "Travel"])
        dialog.list_widget.setCurrentRow(1)  # Select "Travel"

        from PyQt5.QtWidgets import QMessageBox

        with patch(
            "expense_tracker_app.dialogs.QMessageBox.question",
            return_value=QMessageBox.No,
        ):
            initial_categories = mock_dm.categories.copy()
            dialog.remove_category()

            # Should not remove anything
            assert mock_dm.categories == initial_categories


class TestAddExpenseDialog:
    @pytest.mark.gui
    def test_init(self, qapp):
        categories = ["Food", "Travel"]
        dialog = AddExpenseDialog(categories)

        assert dialog.category_dropdown.count() == 2
        assert dialog.category_dropdown.itemText(0) == "Food"

    @pytest.mark.gui
    def test_get_data_valid(self, qapp):
        categories = ["Food", "Travel"]
        dialog = AddExpenseDialog(categories)

        dialog.amount_input.setText("25.50")
        dialog.desc_input.setText("Test expense")
        # Calendar defaults to current date

        data = dialog.get_data()

        assert data is not None
        assert data["amount"] == 25.50
        assert data["description"] == "Test expense"
        assert data["category"] in ["Food", "Travel"]

    @pytest.mark.gui
    def test_get_data_invalid_amount(self, qapp):
        categories = ["Food"]
        dialog = AddExpenseDialog(categories)

        dialog.amount_input.setText("invalid")

        with patch("PyQt5.QtWidgets.QMessageBox.warning") as mock_warning:
            data = dialog.get_data()

            assert data is None
            mock_warning.assert_called_once()

    @pytest.mark.gui
    def test_validate_inputs_valid(self, qapp):
        categories = ["Food"]
        dialog = AddExpenseDialog(categories)

        dialog.amount_input.setText("25.50")
        dialog.desc_input.setText("Valid expense")

        assert dialog.validate_inputs() is True

    @pytest.mark.gui
    def test_validate_inputs_invalid_amount(self, qapp):
        categories = ["Food"]
        dialog = AddExpenseDialog(categories)

        dialog.amount_input.setText("invalid")
        dialog.desc_input.setText("Valid expense")

        assert dialog.validate_inputs() is False

    @pytest.mark.gui
    def test_validate_inputs_negative_amount(self, qapp):
        categories = ["Food"]
        dialog = AddExpenseDialog(categories)

        dialog.amount_input.setText("-10.0")
        dialog.desc_input.setText("Valid expense")

        assert dialog.validate_inputs() is False

    @pytest.mark.gui
    def test_validate_inputs_empty_description(self, qapp):
        categories = ["Food"]
        dialog = AddExpenseDialog(categories)

        dialog.amount_input.setText("25.50")
        dialog.desc_input.setText("")

        assert dialog.validate_inputs() is False
