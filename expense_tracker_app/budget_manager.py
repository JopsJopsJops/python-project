"""
Budget management and alert system for Expense Tracker.
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)


class BudgetManager:
    """Manages category budgets and spending alerts."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.budgets: Dict[str, float] = {}  # category -> budget_amount
        self.alerts: List[str] = []
        self.budget_file = "budgets.json"
        
        # Load existing budgets when initialized
        self.load_budgets()
    
    def load_budgets(self):
        """Load budgets from persistent storage."""
        if not os.path.exists(self.budget_file):
            logger.info("💰 No existing budget file found, starting fresh")
            return
        
        try:
            with open(self.budget_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.budgets = data.get("budgets", {})
                
                # Log budget period info
                budget_period = data.get("budget_period", "monthly")
                last_updated = data.get("last_updated", "unknown")
                
                logger.info(f"💰 Loaded {len(self.budgets)} {budget_period} budgets (last updated: {last_updated})")
                
        except Exception as e:
            logger.error(f"❌ Failed to load budgets: {e}")
            self.budgets = {}

    def save_budgets(self):
        """Save budgets to persistent storage with metadata."""
        try:
            data = {
                "budgets": self.budgets,
                "last_updated": datetime.now().isoformat(),
                "budget_period": "monthly",  # Explicitly state this is monthly budgeting
                "description": "Monthly category budgets - resets conceptually each month",
                "version": "1.0"
            }
            
            with open(self.budget_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"💾 Saved {len(self.budgets)} monthly budgets to {self.budget_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save budgets: {e}")
            return False

    def set_budget(self, category: str, amount: float) -> bool:
        """Set monthly budget for a category (case-insensitive)."""
        if amount < 0:
            logger.warning(f"Invalid budget amount for {category}: {amount}")
            return False
        
        # Normalize the category name (use existing case if available)
        normalized_category = self._normalize_category_name(category)
        
        self.budgets[normalized_category] = amount
        
        # Save immediately after setting budget
        success = self.save_budgets()
        
        if success:
            logger.info(f"💰 Monthly budget set for {normalized_category}: ₱{amount:,.2f}")
        else:
            logger.error(f"❌ Budget set for {normalized_category} but failed to save!")
            
        return success

    def _normalize_category_name(self, category: str) -> str:
        """Normalize category name using case-insensitive matching."""
        category_lower = category.lower()
        
        # Check if we already have this category (case-insensitive)
        for existing_category in self.budgets.keys():
            if existing_category.lower() == category_lower:
                return existing_category  # Return the existing case
        
        # Check in data manager categories
        if hasattr(self.data_manager, 'categories'):
            for existing_category in self.data_manager.categories:
                if existing_category.lower() == category_lower:
                    return existing_category  # Return the existing case
        
        # Check in expense categories
        all_expenses = self.data_manager.list_all_expenses()
        expense_categories = set(exp.get('category') for exp in all_expenses)
        for existing_category in expense_categories:
            if existing_category.lower() == category_lower:
                return existing_category  # Return the existing case
        
        # If no match found, use the provided category as-is
        return category

    def remove_budget(self, category: str) -> bool:
        """Remove budget for a category."""
        normalized_category = self._normalize_category_name(category)
        
        if normalized_category in self.budgets:
            del self.budgets[normalized_category]
            
            # Save immediately after removal
            success = self.save_budgets()
            
            if success:
                logger.info(f"🗑️ Monthly budget removed for {normalized_category}")
            else:
                logger.error(f"❌ Budget removed for {normalized_category} but failed to save!")
                
            return success
        return False
    
    def check_budget_alerts(self):
        """Check for budget alerts - FIXED: No red alert for 'no budgets' message"""
        alerts = []
        
        # Check if we have any budgets at all
        if not self.budgets:
            # This is just informational, not an alert - don't add to alerts list
            # We'll handle this separately in the UI
            return alerts
        
        current_month = datetime.now().strftime("%Y-%m")
        
        # Check each budget
        for category, budget_limit in self.budgets.items():
            monthly_spending = self._get_monthly_spending(category, current_month)
            
            if monthly_spending > budget_limit:
                # This is a real budget violation - red alert
                over_amount = monthly_spending - budget_limit
                alerts.append(
                    f"🚨 Monthly budget exceeded for {category}! "
                    f"Spent ₱{monthly_spending:,.2f} of ₱{budget_limit:,.2f} this month "
                    f"(₱{over_amount:,.2f} over budget)"
                )
            elif monthly_spending > budget_limit * 0.8:
                # Warning alert (approaching budget)
                alerts.append(
                    f"⚠️ Approaching budget limit for {category}: "
                    f"₱{monthly_spending:,.2f} of ₱{budget_limit:,.2f} "
                    f"({monthly_spending/budget_limit*100:.1f}%)"
                )
        
        return alerts
    
    def _get_monthly_spending(self, category: str, month: str) -> float:
        """Calculate monthly spending for a category (case-insensitive)."""
        try:
            # Use the existing list_all_expenses method from data_manager
            all_expenses = self.data_manager.list_all_expenses()
            monthly_total = 0.0
            
            logger.debug(f"🔍 Checking {len(all_expenses)} total expenses for category: {category}, month: {month}")
            
            for expense in all_expenses:
                expense_category = expense.get('category', '')
                expense_date = expense.get('date', '')
                expense_amount = expense.get('amount', 0)
                
                # Check if this expense belongs to our category (CASE-INSENSITIVE) and current month
                if (expense_category.lower() == category.lower() and 
                    expense_date.startswith(month)):
                    try:
                        monthly_total += float(expense_amount)
                        logger.debug(f"   ➕ Added expense: {expense_category} - ₱{expense_amount} on {expense_date}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"   ❌ Invalid amount for expense: {expense_amount} - {e}")
                        continue
                
            logger.debug(f"📈 Monthly spending for {category} in {month}: ₱{monthly_total:,.2f}")
            return monthly_total
            
        except Exception as e:
            logger.error(f"❌ Error calculating monthly spending for {category}: {e}")
            return 0.0
    
    def get_budget_progress(self, category: str) -> Dict[str, float]:
        """Get monthly budget progress for a category."""
        current_month = datetime.now().strftime("%Y-%m")
        spent = self._get_monthly_spending(category, current_month)
        budget = self.budgets.get(category, 0)
        
        return {
            'spent': spent,
            'budget': budget,
            'remaining': max(0, budget - spent),
            'percentage': (spent / budget * 100) if budget > 0 else 0,
            'month': current_month  # Include month for clarity
        }
    
    def get_all_budgets(self) -> Dict[str, Dict[str, float]]:
        """Get progress for all monthly budgets."""
        return {
            category: self.get_budget_progress(category)
            for category in self.budgets
        }
    
    def get_budget_summary(self) -> Dict:
        """Get complete monthly budget summary with alerts."""
        current_month = datetime.now().strftime("%B %Y")  # e.g., "October 2024"
        
        return {
            'budgets': self.get_all_budgets(),
            'alerts': self.check_budget_alerts(),
            'total_budget_categories': len(self.budgets),
            'budget_period': f"Monthly ({current_month})",
            'description': "Budgets reset tracking each month"
        }
    
    def get_budgets_count(self) -> int:
        """Get number of active monthly budgets."""
        return len(self.budgets)