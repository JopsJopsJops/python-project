# conftest.py
import os
import sys
import tempfile
from unittest.mock import Mock

import pytest
from PyQt5.QtWidgets import QApplication

from expense_tracker_app.data_manager import DataManager

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_configure(config):
    """Register custom markers to avoid warnings."""
    config.addinivalue_line(
        "markers", "gui: marks tests as GUI tests (require display)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (no GUI required)"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


@pytest.fixture(scope="session")
def qapp():
    """QApplication fixture for PyQt tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't call app.quit() here as it can interfere with other tests


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing"""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def temp_excel_file():
    """Create a temporary Excel file for testing"""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False)
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file for testing"""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False)
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_data_manager():
    """Create a mock DataManager for testing."""
    mock_dm = Mock(spec=DataManager)
    mock_dm.categories = ["Food", "Transport", "Entertainment"]
    mock_dm.expenses = {
        "Food": [
            {"amount": 25.50, "date": "2023-01-15", "description": "Lunch"},
            {"amount": 15.00, "date": "2023-01-20", "description": "Coffee"},
        ],
        "Transport": [
            {"amount": 45.00, "date": "2023-01-10", "description": "Bus pass"}
        ],
    }
    mock_dm.get_all_expenses.return_value = mock_dm.expenses
    mock_dm.get_category_subtotals.return_value = {"Food": 40.50, "Transport": 45.00}
    mock_dm.get_grand_total.return_value = 85.50
    mock_dm.has_expenses.return_value = True
    mock_dm.get_monthly_totals.return_value = {"2023-01": 85.50}
    mock_dm.get_all_categories.return_value = ["Food", "Transport", "Entertainment"]
    return mock_dm


@pytest.fixture
def sample_expense_data():
    """Sample expense data for testing."""
    return [
        {
            "category": "Food",
            "amount": 25.50,
            "description": "Lunch",
            "date": "2023-01-15",
        },
        {
            "category": "Transport",
            "amount": 45.00,
            "description": "Bus pass",
            "date": "2023-01-10",
        },
    ]
