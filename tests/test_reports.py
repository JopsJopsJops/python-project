# test_reports.py
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from expense_tracker_app.reports import ReportService


class TestReportService:
    @pytest.mark.unit
    def test_init(self):
        """Test ReportService initialization"""
        mock_dm = Mock()
        service = ReportService(mock_dm)
        assert service.data_manager == mock_dm

    @pytest.mark.unit
    def test_generate_summary_report(self):
        """Test summary report generation"""
        mock_dm = Mock()
        mock_dm.list_all_expenses.return_value = [
            {
                "category": "Food",
                "amount": 25.50,
                "date": "2023-01-01",
                "description": "Lunch",
            }
        ]

        service = ReportService(mock_dm)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(ReportService, "export_to_pdf") as mock_export:
                mock_export.return_value = temp_path

                result = service.generate_summary_report(temp_path)

                assert result == temp_path
                mock_dm.list_all_expenses.assert_called_once()
                mock_export.assert_called_once()
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_generate_monthly_report(self):
        """Test monthly report generation"""
        mock_dm = Mock()
        mock_dm.list_all_expenses.return_value = [
            {
                "category": "Food",
                "amount": 25.50,
                "date": "2023-01-01",
                "description": "Lunch",
            },
            {
                "category": "Travel",
                "amount": 100.00,
                "date": "2023-02-01",
                "description": "Bus",
            },
        ]

        service = ReportService(mock_dm)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(ReportService, "export_to_pdf") as mock_export:
                mock_export.return_value = temp_path

                result = service.generate_monthly_report("2023-01", temp_path)

                assert result == temp_path
                mock_export.assert_called_once_with(
                    [
                        {
                            "category": "Food",
                            "amount": 25.50,
                            "date": "2023-01-01",
                            "description": "Lunch",
                        }
                    ],
                    temp_path,
                )
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_generate_category_report(self):
        """Test category report generation"""
        mock_dm = Mock()
        mock_dm.get_sorted_expenses.return_value = {
            "Food": [{"amount": 25.50, "date": "2023-01-01", "description": "Lunch"}]
        }

        service = ReportService(mock_dm)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(ReportService, "export_to_pdf") as mock_export:
                mock_export.return_value = temp_path

                result = service.generate_category_report("Food", temp_path)

                assert result == temp_path
                mock_export.assert_called_once_with(
                    [{"amount": 25.50, "date": "2023-01-01", "description": "Lunch"}],
                    temp_path,
                )
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_iter_rows_from_data_dict(self):
        """Test row iteration from dictionary data"""
        data = {
            "Food": [{"amount": 25.50, "date": "2023-01-01", "description": "Lunch"}],
            "Travel": [{"amount": 100.00, "date": "2023-01-02", "description": "Bus"}],
        }

        rows = ReportService._iter_rows_from_data(data)

        assert len(rows) == 2
        assert rows[0]["category"] == "Food"
        assert rows[0]["amount"] == 25.50
        assert rows[1]["category"] == "Travel"
        assert rows[1]["amount"] == 100.00

    @pytest.mark.unit
    def test_iter_rows_from_data_list(self):
        """Test row iteration from list data"""
        data = [
            {
                "category": "Food",
                "amount": 25.50,
                "date": "2023-01-01",
                "description": "Lunch",
            },
            {
                "category": "Travel",
                "amount": 100.00,
                "date": "2023-01-02",
                "description": "Bus",
            },
        ]

        rows = ReportService._iter_rows_from_data(data)

        assert len(rows) == 2
        assert rows[0]["category"] == "Food"
        assert rows[1]["category"] == "Travel"

    @pytest.mark.unit
    def test_iter_rows_from_data_empty(self):
        """Test row iteration with empty data"""
        rows = ReportService._iter_rows_from_data({})
        assert rows == []

        rows = ReportService._iter_rows_from_data([])
        assert rows == []

        rows = ReportService._iter_rows_from_data(None)
        assert rows == []

    @pytest.mark.unit
    def test_iter_rows_from_data_invalid(self):
        """Test row iteration with invalid data"""
        rows = ReportService._iter_rows_from_data("invalid")
        assert rows == []

    @pytest.mark.unit
    def test_export_to_csv_success(self):
        """Test successful CSV export"""
        data = [
            {
                "category": "Food",
                "amount": 25.50,
                "date": "2023-01-01",
                "description": "Lunch",
            }
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            result = ReportService.export_to_csv(data, temp_path)

            assert result == temp_path
            assert os.path.exists(temp_path)

            # Verify file content
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "category,amount,date,description" in content
                assert "Food,25.5,2023-01-01,Lunch" in content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_export_to_csv_empty_data(self):
        """Test CSV export with empty data"""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            result = ReportService.export_to_csv([], temp_path)

            assert result == temp_path
            assert os.path.exists(temp_path)

            # Verify file has only headers
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "category,amount,date,description" in content
                lines = content.strip().split("\n")
                assert len(lines) == 1  # Only headers
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_export_to_csv_exception(self):
        """Test CSV export exception handling"""
        with patch("builtins.open", side_effect=Exception("File error")), patch(
            "expense_tracker_app.reports.QMessageBox.warning"
        ) as mock_warning:

            result = ReportService.export_to_csv([], "invalid/path.csv")

            assert result is None
            mock_warning.assert_called_once()

    @pytest.mark.unit
    def test_export_to_excel_success(self):
        """Test successful Excel export"""
        data = [
            {
                "category": "Food",
                "amount": 25.50,
                "date": "2023-01-01",
                "description": "Lunch",
            }
        ]

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            result = ReportService.export_to_excel(data, temp_path)

            assert result == temp_path
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_export_to_excel_empty_data(self):
        """Test Excel export with empty data"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_path = f.name

        try:
            result = ReportService.export_to_excel([], temp_path)

            assert result == temp_path
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_export_to_excel_exception(self):
        """Test Excel export exception handling"""
        with patch(
            "expense_tracker_app.reports.xlsxwriter.Workbook",
            side_effect=Exception("Excel error"),
        ), patch("expense_tracker_app.reports.QMessageBox.warning") as mock_warning:

            result = ReportService.export_to_excel([], "test.xlsx")

            assert result is None
            mock_warning.assert_called_once()

    @pytest.mark.unit
    def test_export_to_pdf_success(self):
        """Test successful PDF export"""
        data = [
            {
                "category": "Food",
                "amount": 25.50,
                "date": "2023-01-01",
                "description": "Lunch",
            }
        ]

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = ReportService.export_to_pdf(data, temp_path)

            assert result == temp_path
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_export_to_pdf_empty_data(self):
        """Test PDF export with empty data"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name

        try:
            result = ReportService.export_to_pdf([], temp_path)

            assert result == temp_path
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    @pytest.mark.unit
    def test_export_to_pdf_exception(self):
        """Test PDF export exception handling"""
        with patch(
            "expense_tracker_app.reports.SimpleDocTemplate",
            side_effect=Exception("PDF error"),
        ), patch("expense_tracker_app.reports.QMessageBox.warning") as mock_warning:

            result = ReportService.export_to_pdf([], "test.pdf")

            assert result is None
            mock_warning.assert_called_once()

    @pytest.mark.unit
    def test_generate_summary_report_no_data_manager(self):
        """Test summary report without data manager"""
        service = ReportService()
        result = service.generate_summary_report()
        assert result is None

    @pytest.mark.unit
    def test_generate_monthly_report_no_data_manager(self):
        """Test monthly report without data manager"""
        service = ReportService()
        result = service.generate_monthly_report("2023-01")
        assert result is None

    @pytest.mark.unit
    def test_generate_category_report_no_data_manager(self):
        """Test category report without data manager"""
        service = ReportService()
        result = service.generate_category_report("Food")
        assert result is None
