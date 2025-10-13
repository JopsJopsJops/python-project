from PyQt5.QtWidgets import QMessageBox
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import xlsxwriter
import csv
import logging

logger = logging.getLogger(__name__)


class ReportService:
    """Handles exporting expense data into CSV, Excel, and PDF formats."""

    def __init__(self, data_manager=None):
        self.data_manager = data_manager

    def generate_summary_report(self, filename=None):
        """Generate summary report using instance data manager."""
        if self.data_manager:
            data = self.data_manager.list_all_expenses()
            return self.export_to_pdf(data, filename)
        return None

    def generate_monthly_report(self, month, filename=None):
        """Generate monthly report using instance data manager."""
        if self.data_manager:
            expenses = self.data_manager.list_all_expenses()
            monthly_data = [e for e in expenses if e.get("date", "").startswith(month)]
            return self.export_to_pdf(monthly_data, filename)
        return None

    def generate_category_report(self, category, filename=None):
        """Generate category report using instance data manager."""
        if self.data_manager:
            expenses = self.data_manager.get_sorted_expenses()
            category_data = expenses.get(category, [])
            return self.export_to_pdf(category_data, filename)
        return None

    def _iter_rows_from_data(data_rows):
        """
        Normalize data_rows into a flat list of row dicts with keys:
        category, amount, date, description
        """
        rows = []
        if not data_rows:
            return rows

        # dict form: {category: [records]}
        if isinstance(data_rows, dict):
            for cat, recs in data_rows.items():
                for r in recs:
                    if isinstance(r, dict):
                        row = dict(r)
                        row.setdefault("category", cat)
                        rows.append(row)
                    elif isinstance(r, (list, tuple)):
                        try:
                            rows.append(
                                {
                                    "category": cat,
                                    "amount": float(r[0]) if len(r) > 0 else 0.0,
                                    "date": str(r[1]) if len(r) > 1 else "",
                                    "description": str(r[2]) if len(r) > 2 else "",
                                }
                            )
                        except Exception:
                            continue

        # list form: [records]
        elif isinstance(data_rows, list):
            for r in data_rows:
                if isinstance(r, dict):
                    rows.append(r)
                elif isinstance(r, (list, tuple)):
                    try:
                        rows.append(
                            {
                                "category": (
                                    str(r[0]) if len(r) > 0 else "Uncategorized"
                                ),
                                "amount": float(r[1]) if len(r) > 1 else 0.0,
                                "date": str(r[2]) if len(r) > 2 else "",
                                "description": str(r[3]) if len(r) > 3 else "",
                            }
                        )
                    except Exception:
                        continue
        return rows

    @staticmethod
    def export_to_csv(data_rows, filename=None):
        headers = ["category", "amount", "date", "description"]
        logger.info("Starting CSV export -> %s", filename)

        try:
            rows = ReportService._iter_rows_from_data(data_rows)
            with open(filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in rows:
                    writer.writerow(
                        [
                            r.get("category", ""),
                            r.get("amount", 0),
                            r.get("date", ""),
                            r.get("description", ""),
                        ]
                    )
            logger.info("CSV export successful: %s", filename)
            return filename
        except Exception as e:
            logger.exception("CSV export failed: %s", e)
            QMessageBox.warning(None, "Export Failed", f"CSV export failed: {e}")
            return None

    @staticmethod
    def export_to_excel(data_rows, filename=None):
        headers = ["category", "amount", "date", "description"]
        logger.info("Starting Excel export -> %s", filename)

        try:
            rows = ReportService._iter_rows_from_data(data_rows)
            workbook = xlsxwriter.Workbook(filename)
            ws = workbook.add_worksheet("Expenses")

            header_fmt = workbook.add_format({"bold": True, "bg_color": "#dce6f1"})
            for c, h in enumerate(headers):
                ws.write(0, c, h, header_fmt)

            for row, r in enumerate(rows, start=1):
                ws.write(row, 0, r.get("category", ""))
                ws.write(row, 1, r.get("amount", 0))
                ws.write(row, 2, r.get("date", ""))
                ws.write(row, 3, r.get("description", ""))

            ws.set_column("A:A", 20)
            ws.set_column("B:B", 12)
            ws.set_column("C:C", 15)
            ws.set_column("D:D", 30)
            workbook.close()

            logger.info("Excel export successful: %s", filename)
            return filename
        except Exception as e:
            logger.exception("Excel export failed: %s", e)
            QMessageBox.warning(None, "Export Failed", f"Excel export failed: {e}")
            return None

    @staticmethod
    def export_to_pdf(data_rows, filename=None):
        headers = ["category", "amount", "date", "description"]
        logger.info("Starting PDF export -> %s", filename)

        try:
            rows = ReportService._iter_rows_from_data(data_rows)

            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = [Paragraph("Expense Report", styles["Title"])]

            data = [headers]
            for r in rows:
                data.append(
                    [
                        r.get("category", ""),
                        f"{r.get('amount', 0)}",
                        r.get("date", ""),
                        r.get("description", ""),
                    ]
                )

            table = Table(data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ]
                )
            )

            elements.append(table)
            doc.build(elements)

            logger.info("PDF export successful: %s", filename)
            return filename
        except Exception as e:
            logger.exception("PDF export failed: %s", e)
            QMessageBox.warning(None, "Export Failed", f"PDF export failed: {e}")
            return None
