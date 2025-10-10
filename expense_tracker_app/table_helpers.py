def calculate_subtotal(records):
    """Return subtotal of a list of expense records."""
    return sum(rec.get("amount", 0.0) or 0.0 for rec in records)


def format_expense_row(category, record):
    """Return a dict for an expense row (used in QTableWidget)."""
    return {
        "category": category,
        "amount": f"{record.get('amount', 0.0):.2f}",
        "date": record.get("date", ""),
        "description": record.get("description", "")
    }


def format_total_row(category_name, subtotal, is_grand=False):
    """Return a dict for subtotal or grand total row."""
    if is_grand:
        return {
            "category": "Grand Total",
            "amount": f"₱{subtotal:,.2f}",
            "description": "",
            "is_grand_total": True
        }
    else:
        return {
            "category": category_name,
            "amount": f"₱{subtotal:,.2f}",
            "description": "Subtotal",
            "is_grand_total": False
        }


def prepare_chart_data(categories, amounts, top_n=5):
    """Sort categories+amounts and combine small ones into 'Others'."""
    sorted_data = sorted(zip(categories, amounts),
                         key=lambda x: x[1], reverse=True)
    cats_sorted, amts_sorted = zip(*sorted_data)
    top_categories = list(cats_sorted[:top_n])
    top_amounts = list(amts_sorted[:top_n])
    if len(cats_sorted) > top_n:
        top_categories.append("Others")
        top_amounts.append(sum(amts_sorted[top_n:]))
    return top_categories, top_amounts


def aggregate_category_totals(expenses_by_category):
    """Aggregate total per category from {category: [records]} dict."""
    categories, amounts = [], []
    for category, records in expenses_by_category.items():
        subtotal = calculate_subtotal(records)
        if subtotal > 0:
            categories.append(category)
            amounts.append(subtotal)
    return categories, amounts


def prepare_trend_data(monthly_totals):
    """Prepare sorted months and their totals for trend plotting."""
    months = sorted(monthly_totals.keys())
    totals = [monthly_totals[m] for m in months]
    return months, totals
