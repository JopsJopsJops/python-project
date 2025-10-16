"""
Budget management and alert system for Expense Tracker.
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BudgetManager:
    """Manages category budgets and spending alerts."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.budgets: Dict[str, float] = {}  # category -> budget_amount
        self.alerts: List[str] = []
    
    def set_budget(self, category: str, amount: float) -> bool:
        """Set monthly budget for a category (case-insensitive)."""
        if amount < 0:
            logger.warning(f"Invalid budget amount for {category}: {amount}")
            return False
        
        # Normalize the category name (use existing case if available)
        normalized_category = self._normalize_category_name(category)
        
        self.budgets[normalized_category] = amount
        logger.info(f"Budget set for {normalized_category}: ₱{amount:,.2f}")
        return True
    
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
        if category in self.budgets:
            del self.budgets[category]
            logger.info(f"Budget removed for {category}")
            return True
        return False
    
    def check_budget_alerts(self) -> List[str]:
        """Check for budget exceedances and return alerts."""
        self.alerts.clear()
        current_month = datetime.now().strftime("%Y-%m")
        
        # DEBUG: Log what budgets we're checking
        logger.debug(f"💰 Checking budgets for categories: {list(self.budgets.keys())}")
        
        for category, budget in self.budgets.items():
            monthly_spending = self._get_monthly_spending(category, current_month)
            
            logger.debug(f"📊 Category: {category}, Budget: ₱{budget:,.2f}, Spent: ₱{monthly_spending:,.2f}")
            
            if monthly_spending > budget:
                overspend = monthly_spending - budget
                alert_msg = (
                    f"🚨 Budget exceeded for {category}! "
                    f"Spent ₱{monthly_spending:,.2f} of ₱{budget:,.2f} "
                    f"(₱{overspend:,.2f} over budget)"
                )
                self.alerts.append(alert_msg)
                logger.warning(f"🔴 {alert_msg}")
            
            elif monthly_spending > budget * 0.8:  # 80% threshold
                warning_msg = (
                    f"⚠️  Close to budget limit for {category}. "
                    f"Spent ₱{monthly_spending:,.2f} of ₱{budget:,.2f}"
                )
                self.alerts.append(warning_msg)
                logger.info(f"🟡 {warning_msg}")
        
        # Log if no alerts
        if not self.alerts:
            logger.info("✅ All budgets are within limits")
            
        return self.alerts
    
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
        """Get budget progress for a category."""
        current_month = datetime.now().strftime("%Y-%m")
        spent = self._get_monthly_spending(category, current_month)
        budget = self.budgets.get(category, 0)
        
        return {
            'spent': spent,
            'budget': budget,
            'remaining': max(0, budget - spent),
            'percentage': (spent / budget * 100) if budget > 0 else 0
        }
    
    def get_all_budgets(self) -> Dict[str, Dict[str, float]]:
        """Get progress for all budgets."""
        return {
            category: self.get_budget_progress(category)
            for category in self.budgets
        }
    
    def get_budget_summary(self) -> Dict:
        """Get complete budget summary with alerts."""
        return {
            'budgets': self.get_all_budgets(),
            'alerts': self.check_budget_alerts(),
            'total_budget_categories': len(self.budgets)
        }
    