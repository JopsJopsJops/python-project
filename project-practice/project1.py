from datetime import datetime
import csv
from PyQt5.QtWidgets import QInputDialog,QMessageBox

categories = [
    "Food", "Medical", "Utilities", "Travel",
      "Clothing", "Transportation", "Vehicle"
]

expenses = {category: [] for category in categories}

last_deleted = None

def menu_option():
    print("\nChoose from categories")
    for index_number, category_name in enumerate(categories, 1):
        print(f"{index_number}. {category_name}")
    print(f"{len(categories)+1}. Return to menu")


def get_subtotal(records):
        return sum(float(r['amount']) for r in records)


def get_sorted_expenses():
    all_expenses = [
     (category, record_index, r)
     for category, records in expenses.items()
     for record_index, r in enumerate(records)
    ]
    return sorted(all_expenses, key=lambda x: datetime.strptime(x[2]['date'], "%m-%d-%Y"))


def add_new_expense():
    while True:
        menu_option()
        try:
            choice = int(input("\nChoose the number of category of your expense: "))
            if 1 <= choice <= len(categories):
                try:   
                    amount = float(input(f"{categories[choice-1]}: $"))
                except ValueError:
                    print("Invalid input. Enter a number.")  
                    continue

                if amount <= 0:
                    print("Amount must be greater than zero.")
                    continue

                while True:
                    date = input("Enter date (MM-DD-YYYY) or leave blank for today:")
                    if not date:
                        date = datetime.now().strftime("%m-%d-%Y")
                        break
                    try:
                         datetime.strptime(date,"%m-%d-%Y")
                         break
                    except ValueError:
                         print("Invalid date format. Please use MM-DD-YYYY.")
                
                description = input("Enter description: ")

                expenses[categories[choice-1]].append({
                    "amount": amount,
                    "date" : date,
                    "description": description 
                })
                export_expenses(silent=True)

            elif choice == len(categories)+1:
                return
            else: 
                print("Invalid choice. Try again")
        except ValueError:
            print("Invalid input. Enter a number.")
        

def view_expense_by_category():
    for category, records in expenses.items():
            if records:
                print(f"\n{category}:")
                for r in sorted(records, key=lambda x: datetime.strptime(x['date'], "%m-%d-%Y")):
                     print(f" ${r['amount']:.2f} on {r['date']} - {r['description']}")
                                           

def view_total_expenses():
    print("\n==== Your Total Expense ====")
    total = 0
    for category, records in expenses.items():
                subtotal = get_subtotal(records)
                if subtotal > 0:
                    print(f"{category:<15}: ${subtotal:>10.2f}")
                    total += subtotal
    print("----------------------------")
    print(f"{'Grand Total':<15}: ${total:>10.2f}")


def export_expenses(filename):
    #  with open("expenses.csv", "w", newline="") as files:
    #       writer = csv.writer(files)
    #       writer.writerow(["Category", "Amount", "Date", "Description"])
    #       for category, records in expenses.items():
    #            for r in sorted(records, key=lambda x: datetime.strptime(x['date'], "%m-%d-%Y")):
    #                 writer.writerow([category, f"{r['amount']:.2f}", r['date'], r['description']])
    #  if not silent:
    #     print("\nCsv file has been save successfully. Goodbye!")

    with open(filename, "w", newline="", encoding= "utf-8") as files:
          writer = csv.writer(files)
          writer.writerow(["Category", "Amount", "Date", "Description"])
          for category, records in expenses.items():
               for r in sorted(records, key=lambda x: datetime.strptime(x['date'], "%m-%d-%Y")):
                    writer.writerow([category, f"{r['amount']:.2f}", r['date'], r['description']])
     

def import_expenses(filename):
    #  try:
    #       with open("expenses.csv", "r") as files:
    #            reader = csv.DictReader(files)
    #            count = 0
    #            for row in reader:
    #                 expenses[row["Category"]].append({
    #                      "amount": float(row["Amount"]),
    #                      "date": row["Date"],
    #                      "description": row["Description"]
    #                 })
    #                 count += 1
    #            print(f"\nCsv file has been loaded. {count} expense(s) imported.")
    #  except FileNotFoundError:
    #     print("\nNo saved expenses found.")
    global expenses
    expenses == {}
    try:
        with open(filename, "r") as files:
            reader = csv.DictReader(files)
            count = 0
            for row in reader:
                category = row["Category"]
                if category not in expenses:
                    expenses[category] = []
                expenses["Category"].append({
                        "amount": float(row["Amount"]),
                        "date": row["Date"],
                        "description": row["Description"]
                })
    except FileNotFoundError:
        expenses = {}



def search_expenses():
     keyword = input(f"\nEnter a search keyword: ")
     print(f"🔍 Searching for '{keyword}'.....")
     found = False
     for category, _, r in get_sorted_expenses():
        if keyword.lower() in r['description'].lower():
            print(f"{category}: ${r['amount']:.2f} on {r['date']} - {r['description']}")
            found = True
     if not found:
        print("No matching expenses found.")


def listing_expense(action="edit", mode="terminal",parent=None):
    sorted_expenses = get_sorted_expenses()
    if not sorted_expenses:
        if mode == "terminal":
            print(f"\nNo expenses to {action}.")
        return None
    
    # for display_idx, (category, _, r) in enumerate(sorted_expenses,1):
    #      print(f"{display_idx}: {category} ${r['amount']:.2f} on {r['date']} - {r['description']}")
     # Display the expenses
    if mode == "terminal":
        for display_idx, (category, _, r) in enumerate(sorted_expenses, 1):
            print(f"{display_idx}: {category} ${r['amount']:.2f} on {r['date']} - {r['description']}")

        try:
            idx = int(input(f"\nEnter # of expense to {action}: "))
            if not (1 <= idx <= len(sorted_expenses)):
                print("Invalid number.")
                return None
        except ValueError:
            print("Invalid input.")
            return None

    elif mode == "gui":
        # Return a list of string labels for GUI selection
        items = [
            f"{display_idx}: {category} ${r['amount']:.2f} on {r['date']} - {r['description']}"
            for display_idx, (category, _, r) in enumerate(sorted_expenses, 1)
        ]

        choice, ok = QInputDialog.getItem(parent, f"{action.capitalize()} Expense",
                                          f"Choose expense to {action}:", items, 0, False)
        if not ok:
            return None
        
        idx = int(choice.split(":")[0])

    # If terminal mode, continue to return the selected record
    category, record_index, record = sorted_expenses[idx - 1]
    return idx, category, record_index, record

    # try:
    #     idx = int(input(f"\nEnter # of expense to {action}: "))
    #     if not (1 <= idx <= len(sorted_expenses)):
    #          print("Invalid number.")
    #          return None
    # except ValueError:
    #     print("Invalid input.")
    #     return None

    # category, record_index, record = sorted_expenses[idx -1]
    # return idx, category, record_index, record


def edit_expense():
    result = listing_expense("edit")
    if not result:
         return
    
    _, category, record_index, record = result

    new_amount = input(f"New amount (leave blank to keep ${record['amount']:.2f}): ")
    if new_amount.strip():
        try:
             record['amount'] = float(new_amount)
        except ValueError:
            print("Invalid amount. Keeping old value.")

    new_date = input(f"New date (MM-DD-YYYY) or leave blank to keep {record['date']}: ")
    if new_date.strip():
        try:
             datetime.strptime(new_date, "%m-%d-%Y")
             record['date'] = new_date
        except ValueError:
             print("Invalid date format. Keeping old date.")

    new_description = input(f"New description (leave blank to keep '{record['description']}'): ")
    if new_description.strip():
           record['description'] = new_description

    expenses[category][record_index] = record
    export_expenses(silent=True)
    print("\nExpense updated successfully.")


def delete_expense():
    global last_deleted
    result = listing_expense("delete")
    if not result:
         return
    user_idx, category, record_index, record = result

    print(f"\nSelected: #{user_idx}: {category} ${record['amount']:.2f} on {record['date']} - {record['description']}")
    choice = input(f"\nAre you sure you want to delete this expense? Y/N: ").lower()
    if choice ==  "y":
         last_deleted = (category, record_index, record)
         expenses[category].pop(record_index)
         export_expenses(silent=True)
         print("\nExpense deleted successfully. Select 'undo' from the main menu to restore it.")
    elif choice == "n":
         print("\nDeletion canceled.")
    else:
         print("Invalid input. Y or N only.")
    

def undo_last_delete():
     global last_deleted
     if not last_deleted:
          print("\nNo expense to restore.")
          return
     category, _, record = last_deleted
     expenses[category].append(record)
     expenses[category].sort(key=lambda x: datetime.strptime(x['date'], "%m-%d-%Y"))
     
     export_expenses(silent=True)
     print(f"Restored: {category} ${record['amount']:.2f} on {record['date']} - {record['description']}")
     last_deleted = None


def main():
    import_expenses()
    while True:
        print("\n====== Expense Tracker. ======")
        print("1. Add new expense")
        print("2. View expenses by category")
        print("3. View total expenses")
        print("4. Search expenses")
        print("5. Edit an expense")
        print("6. Delete an expense")
        print("7. Undo last delete")
        print("8. Save and Exit")
        print("----------------------------")

        try:
            choice = int(input("Choose your number: "))
        except ValueError:
            print("Invalid input. Enter a number.")
            continue

        if choice == 1:
            add_new_expense()
        elif choice == 2:
            view_expense_by_category()
        elif choice == 3:
            view_total_expenses()
        elif choice == 4:
            search_expenses()
        elif choice == 5:
            edit_expense()
        elif choice == 6:
            delete_expense()   
        elif choice == 7:
            undo_last_delete()     
        elif choice == 8:
            export_expenses()
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Thank you for using Expense Tracker.")
            print("~~~~~~~~~~~~~~~~~~~~~~~~")

            break
        else:
            print("Invalid choice")



if __name__ == "__main__":
    main()