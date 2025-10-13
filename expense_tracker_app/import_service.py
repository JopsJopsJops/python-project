import csv
import logging
import os

import openpyxl

logger = logging.getLogger(__name__)


class DataImportService:
    """Handles importing expense data from CSV and Excel."""

    @staticmethod
    def import_from_csv(file_path, data_manager=None):
        """Import expenses from a CSV file into the DataManager."""
        import csv
        import os

        logger.info("Importing from CSV: %s", file_path)
        data = {}
        success = False

        try:
            if not isinstance(file_path, (str, bytes, os.PathLike)):
                raise TypeError(f"Expected file path, got {type(file_path).__name__}")

            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                if "category" not in reader.fieldnames:
                    logger.warning("Invalid CSV format: missing category column")
                    return {}

                for row in reader:
                    try:
                        raw_category = row.get("category", "").strip()
                        category = raw_category if raw_category else "Uncategorized"
                        category = category.lower()  # ✅ normalize

                        try:
                            amount = float(row.get("amount", 0))
                            if amount <= 0:
                                continue
                        except (ValueError, TypeError):
                            continue

                        date = row.get("date", "").strip()
                        description = row.get("description", "").strip()

                        rec = {
                            "amount": amount,
                            "date": date,
                            "description": description,
                        }
                        data.setdefault(category, []).append(rec)

                        if data_manager:
                            data_manager.add_expense(
                                category, amount, date, description
                            )

                    except Exception as e:
                        logger.debug("Error processing CSV row: %s", e)
                        continue

            success = True
            return {"success": True, "data": data}
        except Exception as e:
            logger.error("CSV import failed: %s", e)
            return {"success": False, "data": {}}

    @staticmethod
    def import_from_excel(file_path, data_manager=None):
        """Import expenses from an Excel file into the DataManager."""
        import os

        import openpyxl

        logger.info("Importing from Excel: %s", file_path)
        data = {}
        success = False

        try:
            if not isinstance(file_path, (str, bytes, os.PathLike)):
                raise TypeError(f"Expected file path, got {type(file_path).__name__}")

            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active

            headers = [
                str(c.value).strip().lower() if c.value else "" for c in sheet[1]
            ]
            if "category" not in headers:
                logger.warning("Invalid Excel format: missing category column")
                return {}

            category_idx = headers.index("category")
            amount_idx = headers.index("amount") if "amount" in headers else None
            date_idx = headers.index("date") if "date" in headers else None
            desc_idx = (
                headers.index("description") if "description" in headers else None
            )

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not any(row):
                    continue
                try:
                    raw_category = (
                        row[category_idx] if category_idx < len(row) else None
                    )
                    category = (
                        str(raw_category).strip() if raw_category else "Uncategorized"
                    )
                    category = category.lower()  # ✅ normalize

                    amount_val = (
                        row[amount_idx]
                        if (amount_idx is not None and amount_idx < len(row))
                        else 0
                    )
                    try:
                        amount = float(amount_val)
                        if amount <= 0:
                            continue
                    except (ValueError, TypeError):
                        continue

                    date = (
                        str(row[date_idx])
                        if (
                            date_idx is not None
                            and date_idx < len(row)
                            and row[date_idx]
                        )
                        else ""
                    )
                    description = (
                        str(row[desc_idx])
                        if (
                            desc_idx is not None
                            and desc_idx < len(row)
                            and row[desc_idx]
                        )
                        else ""
                    )

                    rec = {"amount": amount, "date": date, "description": description}
                    data.setdefault(category, []).append(rec)

                    if data_manager:
                        data_manager.add_expense(category, amount, date, description)

                except Exception as e:
                    logger.debug("Error processing Excel row: %s", e)
                    continue

            success = True
            return {"success": True, "data": data}
        except Exception as e:
            logger.error("Excel import failed: %s", e)
            return {"success": False, "data": {}}
