import pytest
import unittest
from unittest.mock import patch, Mock
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys

# Import your modules
from expense_tracker_app.data_manager import DataManager
from expense_tracker_app.dialogs import CategoryDialog

class TestCategoryManagement(unittest.TestCase):
    
    def setUp(self):
        # Create QApplication instance for PyQt tests
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # Clear any persistent data
        self.dm = DataManager()
        self.dm.expenses = {}
        self.dm.categories = ["Uncategorized"]  # Keep only essential categories

    def test_category_normalization(self):
        """Test that categories are properly capitalized"""
        dm = DataManager()
        
        # Test various inputs
        self.assertEqual(dm.normalize_category_name("food"), "Food")
        self.assertEqual(dm.normalize_category_name("FAST FOOD"), "Fast Food")
        self.assertEqual(dm.normalize_category_name("work equipment"), "Work Equipment")

    def test_category_duplicate_detection(self):
        """Test that duplicate categories are detected"""
        dm = DataManager()
        
        # Add a category
        success, message = dm.add_category("Food")
        self.assertTrue(success)
        
        # Try to add duplicate with different case
        success, message = dm.add_category("food")
        self.assertFalse(success)
        self.assertIn("already exists", message)

    def test_remove_category_with_merge(self):
        """Test removing category with merge functionality"""
        dm = self.dm  # Use the cleared DataManager
        
        # Add categories and expenses
        dm.add_category("Food")
        dm.add_category("Dining")
        dm.add_expense("Food", 100, "2024-01-01", "Lunch")
        
        # Remove Food and merge into Dining
        success, message = dm.remove_category("Food", "Dining")
        self.assertTrue(success)
        
        # Check expenses were moved
        self.assertNotIn("Food", dm.expenses)
        self.assertIn("Dining", dm.expenses)
        self.assertEqual(len(dm.expenses["Dining"]), 1) 

    def test_remove_category_merge_flow(self):
        """Test the merge flow without actual UI"""
        dm = DataManager()
        dialog = CategoryDialog(dm)
        
        # Mock the user selection and button clicks
        with patch.object(dialog, 'ask_merge_target', return_value="Dining"):
            with patch.object(dialog.list_widget, 'currentItem') as mock_item:
                mock_item.return_value.text.return_value = "Food"
                
                # Mock that category has expenses
                dm.expenses = {"Food": [{"amount": 100, "date": "2024-01-01", "description": "Lunch"}]}
                dm.categories = ["Food", "Dining"]
                
                # This should trigger merge flow
                dialog.remove_category()
                
                # Verify expenses were moved
                self.assertNotIn("Food", dm.expenses)
                self.assertIn("Dining", dm.expenses)

    def test_remove_category_uncategorized_confirmation(self):
        """Test that move to uncategorized requires confirmation"""
        dm = DataManager()
        dialog = CategoryDialog(dm)
        
        with patch.object(dialog.list_widget, 'currentItem') as mock_item:
            mock_item.return_value.text.return_value = "Food"
            dm.expenses = {"Food": [{"amount": 100, "date": "2024-01-01", "description": "Lunch"}]}
            dm.categories = ["Food"]
            
            # Mock the confirmation dialog to return "No" (user cancels)
            with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QMessageBox.No):
                dialog.remove_category()
                
                # Category should NOT be removed since user cancelled
                self.assertIn("Food", dm.categories)   
    
    def test_remove_empty_category(self):
        """Test removing category with no expenses"""
        dm = DataManager()
        dm.add_category("Test")
        
        success, message = dm.remove_category("Test")
        self.assertTrue(success)
        self.assertNotIn("Test", dm.categories)

    def test_remove_nonexistent_category(self):
        """Test removing category that doesn't exist"""
        dm = DataManager()
        
        success, message = dm.remove_category("Nonexistent")
        self.assertFalse(success)
        self.assertIn("not found", message)

    def test_merge_target_normalization(self):
        """Test that merge targets are also normalized"""
        dm = DataManager()
        dm.add_category("Food")
        dm.add_expense("Food", 100, "2024-01-01", "Lunch")
        
        # Merge into category with different case
        success, message = dm.remove_category("Food", "food")
        self.assertTrue(success)
        # Should merge into "Food" (capitalized)

    def tearDown(self):
        """Clean up after tests"""
        import os
        # Remove test file
        if hasattr(self, 'dm') and os.path.exists("test_expenses.json"):
            os.remove("test_expenses.json")
        if hasattr(self, 'app'):
            self.app.quit()