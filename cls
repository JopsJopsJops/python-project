[1mdiff --git a/tests/test_main.py b/tests/test_main.py[m
[1mindex bdcbd09..819702d 100644[m
[1m--- a/tests/test_main.py[m
[1m+++ b/tests/test_main.py[m
[36m@@ -14,7 +14,7 @@[m [mfrom datetime import datetime[m
 sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))[m
 [m
 [m
[31m-@pytest.mark.unit[m
[32m+[m[32m@pytest.mark.gui[m
 @pytest.fixture[m
 def mock_data_manager():[m
     """Create a mock data manager for testing"""[m
[36m@@ -49,7 +49,7 @@[m [mdef mock_data_manager():[m
     return mock_dm[m
 [m
 [m
[31m-@pytest.mark.unit[m
[32m+[m[32m@pytest.mark.gui[m
 @pytest.fixture[m
 def app():[m
     """Create QApplication instance for testing"""[m
[36m@@ -60,7 +60,7 @@[m [mdef app():[m
     # Don't quit here - let pytest handle cleanup[m
 [m
 [m
[31m-@pytest.mark.unit[m
[32m+[m[32m@pytest.mark.gui[m
 @pytest.fixture[m
 def main_window(mock_data_manager, qtbot):[m
     """Create main window for testing with proper mocking"""[m
[36m@@ -93,7 +93,7 @@[m [mdef main_window(mock_data_manager, qtbot):[m
 class TestMainWindow:[m
     """Comprehensive tests for MainWindow to achieve 100% coverage"""[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.fixture[m
     def main_window_with_ui(self, qtbot):[m
         """Create MainWindow with proper UI mocking"""[m
[36m@@ -153,7 +153,7 @@[m [mclass TestMainWindow:[m
 [m
             yield window[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_main_window_initialization(self, main_window_with_ui):[m
         """Test MainWindow initializes correctly with all components"""[m
         window = main_window_with_ui[m
[36m@@ -163,7 +163,7 @@[m [mclass TestMainWindow:[m
         assert hasattr(window, "dashboard")[m
         assert hasattr(window, "tabs")[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_setup_ui_components(self, main_window_with_ui):[m
         """Test UI setup methods"""[m
         window = main_window_with_ui[m
[36m@@ -178,7 +178,7 @@[m [mclass TestMainWindow:[m
         # Skip testing setup_reports_tab since it has complex UI dependencies[m
         # that are hard to mock completely in tests[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_report_filtering_methods(self, main_window_with_ui):[m
         """Test report filtering functionality"""[m
         window = main_window_with_ui[m
[36m@@ -244,7 +244,7 @@[m [mclass TestMainWindow:[m
         assert len(date_filtered) == 1  # Should only return the Coffee expense[m
         assert date_filtered[0]["description"] == "Coffee"[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_report_view_updates(self, main_window_with_ui):[m
         """Test report view update methods"""[m
         window = main_window_with_ui[m
[36m@@ -281,7 +281,7 @@[m [mclass TestMainWindow:[m
         window.report_table.setRowCount.assert_called()[m
         window.summary_label.setText.assert_called()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_export_functionality(self, main_window_with_ui):[m
         """Test export methods"""[m
         window = main_window_with_ui[m
[36m@@ -330,7 +330,7 @@[m [mclass TestMainWindow:[m
             assert result is True[m
             mock_pdf.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_import_functionality(self, main_window_with_ui):[m
         """Test import methods"""[m
         window = main_window_with_ui[m
[36m@@ -359,7 +359,7 @@[m [mclass TestMainWindow:[m
             window.import_from_excel()[m
             mock_excel_import.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_application_lifecycle(self, main_window_with_ui):[m
         """Test application exit and close events"""[m
         window = main_window_with_ui[m
[36m@@ -390,7 +390,7 @@[m [mclass TestMainWindow:[m
             window.closeEvent(mock_event)[m
             mock_event.accept.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_tab_switching(self, main_window_with_ui):[m
         """Test tab switching functionality"""[m
         window = main_window_with_ui[m
[36m@@ -416,7 +416,7 @@[m [mclass TestMainWindow:[m
         window.refresh_dashboard_on_switch(0)  # Other tab[m
         window.dashboard.update_dashboard.assert_not_called()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_error_handling(self, main_window_with_ui):[m
         """Test error handling scenarios"""[m
         window = main_window_with_ui[m
[36m@@ -451,7 +451,7 @@[m [mclass TestMainWindow:[m
             assert result is False[m
             mock_warning.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_refresh_functionality(self, main_window_with_ui):[m
         """Test refresh methods"""[m
         window = main_window_with_ui[m
[36m@@ -473,19 +473,19 @@[m [mclass TestMainWindow:[m
         window.expense_tracker.refresh_category_dropdowns.assert_called_once()[m
         window.update_report_date_ranges.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_export_with_no_data(self, main_window_with_ui):[m
         # Implement this test[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_pdf_export_with_no_data(self, main_window_with_ui):[m
         # Implement this test[m
         pass[m
 [m
     """Basic MainWindow tests"""[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_main_window_import(self, main_window):[m
         """Test MainWindow initialization - simplified"""[m
         assert main_window is not None[m
[36m@@ -493,114 +493,114 @@[m [mclass TestMainWindow:[m
 [m
     """Test MainWindow functionality"""[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_init(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_create_menus(self, main_window):[m
         """Test menu creation - simplified"""[m
         menubar = main_window.menuBar()[m
         assert menubar is not None[m
         # Remove complex iteration for now[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_setup_reports_tab(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_get_all_expense_dates(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_get_filtered_expenses(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_get_filtered_expenses_with_category_filter(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_get_filtered_expenses_with_date_filter(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_update_report_view(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI attributes missing - needs proper setup")[m
     def test_update_report_date_ranges(self, main_window):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow UI complexity - needs proper mocking")[m
     def test_export_to_excel_or_csv_excel(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_export_to_excel_or_csv_csv(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_export_to_excel_or_csv_cancelled(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_export_to_excel_or_csv_direct_path(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_export_to_pdf(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_export_to_pdf_direct_path(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_import_from_csv(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_import_from_excel(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_exit_application_confirmed(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_exit_application_cancelled(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_close_event_confirmed(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_close_event_cancelled(self):[m
         pass[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_export_with_no_data(self, main_window_with_ui):[m
         """Test export when no expenses exist"""[m
         window = main_window_with_ui[m
[36m@@ -611,7 +611,7 @@[m [mclass TestMainWindow:[m
             assert result is False[m
             mock_info.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_pdf_export_with_no_data(self, main_window_with_ui):[m
         """Test PDF export when no expenses exist"""[m
         window = main_window_with_ui[m
[36m@@ -622,7 +622,7 @@[m [mclass TestMainWindow:[m
             assert result is False[m
             mock_info.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_export_exception_handling(self, main_window_with_ui):[m
         """Test export handles exceptions gracefully"""[m
         window = main_window_with_ui[m
[36m@@ -646,13 +646,13 @@[m [mclass TestMainWindow:[m
             assert result is False[m
             mock_warning.assert_called_once()[m
 [m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     @pytest.mark.skip(reason="MainWindow complexity - fix core first")[m
     def test_import_cancelled(self):[m
         pass[m
 [m
     # In test_main.py - add new tests[m
[31m-    @pytest.mark.unit[m
[32m+[m[32m    @pytest.mark.gui[m
     def test_get_all_expense_dates_with_invalid_dates(self, main_window_with_ui):[m
         """Test date extraction handles invalid dates gracefully"""[m
         window = main_window_with_ui[m
