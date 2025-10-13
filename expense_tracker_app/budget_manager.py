"""
Budget management and alert system for Expense Tracker Pro.
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
        """Set monthly budget for a category."""
        if amount < 0:
            logger.warning(f"Invalid budget amount for {category}: {amount}")
            return False
        
        self.budgets[category] = amount
        logger.info(f"Budget set for {category}: ₱{amount:,.2f}")
        return True
    
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
        
        for category, budget in self.budgets.items():
            monthly_spending = self._get_monthly_spending(category, current_month)
            
            if monthly_spending > budget:
                overspend = monthly_spending - budget
                alert_msg = (
                    f"🚨 Budget exceeded for {category}! "
                    f"Spent ₱{monthly_spending:,.2f} of ₱{budget:,.2f} "
                    f"(₱{overspend:,.2f} over budget)"
                )
                self.alerts.append(alert_msg)
                logger.warning(alert_msg)
            
            elif monthly_spending > budget * 0.8:  # 80% threshold
                warning_msg = (
                    f"⚠️  Close to budget limit for {category}. "
                    f"Spent ₱{monthly_spending:,.2f} of ₱{budget:,.2f}"
                )
                self.alerts.append(warning_msg)
                logger.info(warning_msg)
        
        return self.alerts
    
    def _get_monthly_spending(self, category: str, month: str) -> float:
        """Calculate monthly spending for a category."""
        expenses = self.data_manager.get_expenses_for_category(category)
        monthly_total = 0.0
        
        for expense in expenses:
            if expense.get('date', '').startswith(month):
                try:
                    monthly_total += float(expense.get('amount', 0))
                except (ValueError, TypeError):
                    continue
        
        return monthly_total
    
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