import sys
from PyQt5.QtWidgets import (QApplication, QWidget,
                            QPushButton, QVBoxLayout,
                             QInputDialog,QMessageBox,QTextEdit,
                             QComboBox)
from PyQt5.QtGui import QFontDatabase
from datetime import datetime
import project1
import csv




class ExpenseTracker(QWidget):
            
    def __init__(self):
         super().__init__()

         self.setWindowTitle("Expense Tracker")
         self.setGeometry(200, 200, 400, 300)

         layout = QVBoxLayout()

         self.combo_box = QComboBox()
         self.combo_box.addItems(["Food", "Medical", "Utilities", "Travel",
            "Clothing", "Transportation", "Vehicle"])
         self.combo_box.setEditable(False)

         
         self.text_area = QTextEdit(self)
         self.text_area.setReadOnly(True)
         self.text_area.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
         self.text_area.setMinimumSize(600, 300)
         self.text_area.setHtml("Welcome to the <b>Expense Tracker</b>! <br>" \
         "<br>Easily record, view, and organize your expenses by category and date.<br>" \
         "<br>Track subtotals per category and monitor your overall spending with the grand total summary.")
         layout.addWidget(self.text_area)


         self.view_button = QPushButton("View Expenses")
         self.view_button.clicked.connect(self.show_expense)
         layout.addWidget(self.view_button)


         self.add_button = QPushButton("Add Expense(s)")
         self.add_button.clicked.connect(self.add_expense)
         layout.addWidget(self.add_button)
        
         self.total_expense_button = QPushButton("Show Total Expenses")
         self.total_expense_button.clicked.connect(self.show_total_expense)
         layout.addWidget(self.total_expense_button)

         self.search_button = QPushButton("Search a keyword of expense(s)")
         self.search_button.clicked.connect(self.search_expenses)
         layout.addWidget(self.search_button)

         self.edit_button = QPushButton("Edit an expense(s)")
         self.edit_button.clicked.connect(self.edit_expense)
         layout.addWidget(self.edit_button)

         self.delete_button = QPushButton("Delete an expense(s)")
         self.delete_button.clicked.connect(self.delete_expense)
         layout.addWidget(self.delete_button)

         self.undo_button = QPushButton("Undo last delete")
         self.undo_button.clicked.connect(self.undo_last_delete)
         layout.addWidget(self.undo_button)

         self.exit_button = QPushButton("Save and exit")
         self.exit_button.clicked.connect(self.exit_mode)
         layout.addWidget(self.exit_button)        

         self.setLayout(layout)

         self.last_deleted = None

         self.setStyleSheet("""
           QPushButton{
                  font-family: Verdana;
                  font-size: 15px;
                  background: hsl(183, 42%, 93%);
                  color: hsl(206, 88%, 57%);
                  border-radius: 10px;
                  padding: 5px;
                  border: 2px solid blue;
            }
            QPushButton:hover {
                  border: 3px solid blue;
            }
            QComboBox{
                  font-family: Verdana;
                  font-size: 15px;
                  color: hsl(206, 88%, 57%);
            }                   
           QTextEdit{
               font-size: 15px;
               color: hsl(206, 88%, 57%);
               background: hsl(183, 42%, 93%);
            }                  
            """)            

    def add_expense(self):
        items = [self.combo_box.itemText(i) for i in range(self.combo_box.count())]

        amount, ok = QInputDialog.getDouble(self, "Add Expense", "Enter amount: ")
        if not ok:
            return
        
        category, ok = QInputDialog.getItem(self, "Add Expense", "Choose the category: ", items, 0, False)
        if not ok or not category.strip():
            return
        
        while True:
            date, ok = QInputDialog.getText(self, "Add Expense", "Enter date:(MM-DD-YYYY) ")
            if not ok:
                return
            if not date.strip():
                date = datetime.now().strftime("%m-%d-%Y")
                break
            try:
                    datetime.strptime(date,"%m-%d-%Y")
                    break
            except ValueError:
                    QMessageBox.warning(self, "Error", "Invalid date format. Please use MM-DD-YYYY.")
            continue


        description, ok = QInputDialog.getText(self, "Add Expense", "Enter description: ")
        if not ok or not description.strip():
            return
        

        project1.expenses.setdefault(category, []).append({
                "amount" : amount,
                "date": date,
                "description": description
        })

        project1.export_expenses(silent=True)
        QMessageBox.information(self, "Success", "Expense added successfully!")

        self.show_expense()


    def show_expense(self):
        self.text_area.clear() 
        expenses = project1.get_sorted_expenses()


        grouped = {} 
        for category, record_index, record in expenses: 
            grouped.setdefault(category, []).append(record)

        lines = [] 
        header = f"{'Category':<15} {'Amount':<10} {'Date':<15} {'Description':<30}"
        lines.append(header) 
        lines.append("-" * len(header))

        for category in sorted(grouped): 
            records = sorted(grouped[category], key=lambda r: r['date']) 
            subtotal = 0

            for idx, record in enumerate(records):
                cat_display = category if idx == 0 else "" 
                line = f"{cat_display:<15} {float(record['amount']):<10.2f} {record['date']:<15} {record['description']:<30}"
                lines.append(line) 
                subtotal += float(record['amount'])

            subtotal_line = f"{'-'*len(header)} {'':<15} {'':<30}"
            lines.append(subtotal_line)
            subtotal_line = f"{'Subtotal:':<15} {subtotal:<10.2f}"
            lines.append(f"<b>{subtotal_line}</b>")
            lines.append(f"{'-'*len(header)} {'':<15} {'':<30}")
            lines.append("")

        output = "\n".join(lines) 
        self.text_area.setHtml(f"<pre>{output}</pre>")

    def show_total_expense(self):
        self.text_area.clear()
        expenses = project1.get_sorted_expenses() 

        grouped = {}
        for category, record_index, record in expenses:
            grouped.setdefault(category, []).append(record)

        lines = []
        header = f"{'Category':<15} {'Total Amount':<15}"
        lines.append(header)
        lines.append("-" * len(header))

        grand_total = 0
        for category in sorted(grouped):
            records = grouped[category]
            subtotal = project1.get_subtotal(records) 
            grand_total += subtotal
            line = f"{category:<15} {subtotal:<15.2f}"
            lines.append(line)

        lines.append("-" * len(header))

        total_line = f"{'Grand Total:':<15} {grand_total:<10.2f}"
        lines.append("")
        lines.append(f"<b>{total_line}</b>")

        output = "\n".join(lines)
        self.text_area.setHtml(f"<pre>{output}</pre>")


    def search_expenses(self):
        keyword, ok = QInputDialog.getText(self, "Search", "Enter a keyword:")
        if not ok:
            return
        
        self.text_area.clear()
        self.text_area.setPlainText(f"🔍 Searching for '{keyword}'.....\n")
        found = False
        for category, _, r in project1.get_sorted_expenses():
            if keyword.lower() in r['description'].lower():
                self.text_area.append(f"{category}: ${r['amount']:.2f} on {r['date']} - {r['description']}\n")
                found = True
                self.adjustSize()
        if not found:
            QMessageBox.information(self, "Info","No matching expenses found.")


    def edit_expense(self):
        picked = self.pick_expense("Edit Expense")
        if not picked:
            return
        
        category, record_index, record = picked
        

        new_amount, ok = QInputDialog.getDouble(self, "Edit", f"Enter new amount (current: ${record['amount']:.2f}): ", value=record['amount'])
        if not ok:
            return
        
        try:
                record['amount'] = float(new_amount)
        except ValueError:
                QMessageBox.warning(self, "Error", "Invalid amount. Keeping old value.")

        while True:
            new_date, ok = QInputDialog.getText(self, "Edit", f"New date (MM-DD-YYYY) or leave blank to keep {record['date']}: ")
            if not  ok:
                return
            if not new_date.strip():
                break
            try:
                datetime.strptime(new_date, "%m-%d-%Y")
                record['date'] = new_date
                break
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid date format. Keeping old date.")

        new_description, ok = QInputDialog.getText(self, "Edit", f"New description (leave blank to keep '{record['description']}'): ")
        if not ok:
            return
        if new_description.strip():
            record['description'] = new_description


        project1.expenses[category][record_index] = record
        project1.export_expenses(silent=True)
        QMessageBox.information(self, "Success", "Expense updated successfully.")


    def export_expenses(self,silent=False):
     with open("expenses.csv", "w", newline="") as files:
          writer = csv.writer(files)
          writer.writerow(["Category", "Amount", "Date", "Description"])
          for category, records in project1.expenses.items():
               for r in sorted(records, key=lambda x: datetime.strptime(x['date'], "%m-%d-%Y")):
                    writer.writerow([category, f"{r['amount']:.2f}", r['date'], r['description']])
     if not silent:
        QMessageBox.information(self, "Success","Csv file has been save successfully. Goodbye!")   


    def import_expenses(self):
     try:
          with open("expenses.csv", "r") as files:
               reader = csv.DictReader(files)
               count = 0
               for row in reader:
                    project1.expenses[row["Category"]].append({
                         "amount": float(row["Amount"]),
                         "date": row["Date"],
                         "description": row["Description"]
                    })
                    count += 1
               QMessageBox.information(self, "Success",f"\nCsv file has been loaded. {count} expense(s) imported.")
     except FileNotFoundError:
        QMessageBox.information(self, "Info","No saved expenses found.")


    def pick_expense(self,title):
        expenses = project1.get_sorted_expenses()
        if not expenses:
            QMessageBox.information(self, "Info", "No expenses available.")
            return None
        
        items = [
            f"{i+1}: {cat} ${rec['amount']:.2f} on {rec['date']} - {rec['description']}"
            for i, (cat, rec_idx, rec) in enumerate(expenses)
        ]
        choice, ok = QInputDialog.getItem(self, title, "Select:", items, 0, False)
        if not ok or not choice:
            return None
        
        idx = items.index(choice)
        return expenses[idx]


    def delete_expense(self):
        self.text_area.clear()
        picked = self.pick_expense("Delete Expense")
        if not picked:
            return
        
        category, record_index, record = picked
        

        self.text_area.insertPlainText(f"\nSelected: {category} ${record['amount']:.2f} on {record['date']} - {record['description']}")
        reply = QMessageBox.question(self,"Confirm Delete", "Are you sure you want to delete this expense?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.last_deleted = (category, record_index, record)
            project1.expenses[category].pop(record_index)
            project1.export_expenses(silent=True)
            QMessageBox.information(self,"Success", "Expense deleted successfully! Select 'undo' from the main menu to restore it.")
        else:
            QMessageBox.information(self, "Info","Deletion cancelled.")
            return


    def undo_last_delete(self):
            self.text_area.clear()
            if not self.last_deleted:
                QMessageBox.information(self, "Info", "\nNo expense to restore.")
                return
            
            category, _, record = self.last_deleted
            project1.expenses[category].append(record)
            project1.expenses[category].sort(key=lambda x: datetime.strptime(x['date'], "%m-%d-%Y"))
            
            project1.export_expenses(silent=True)
            self.text_area.insertPlainText(f"Restored: {category} ${record['amount']:.2f} on {record['date']} - {record['description']}")
            self.last_deleted = None

    def exit_mode(self):
        reply = QMessageBox.question(self,"Confirm", "Are you sure you want to save and exit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            project1.export_expenses(silent=True)
            QMessageBox.information(self,"Save successful", "Thank you for using Expenses Diary.")
            QApplication.quit()  


if __name__ == "__main__":

    project1.import_expenses()
    app = QApplication(sys.argv)
    window = ExpenseTracker()
    window.show()
    sys.exit(app.exec_())
