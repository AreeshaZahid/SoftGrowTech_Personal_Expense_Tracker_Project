import sqlite3
import csv
from datetime import datetime
from collections import defaultdict


# ===========================================================
# DATABASE SETUP
# ===========================================================

DB_NAME = "expense_tracker.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ===========================================================
# ADD TRANSACTION
# ===========================================================

def add_transaction(transaction_type):
    print(f"\n--- Add {transaction_type} ---")

    category = input("Enter category: ").strip()

    while True:
        try:
            amount = float(input("Enter amount: "))
            if amount <= 0:
                print("Amount must be greater than 0.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter numbers only.")

    description = input("Enter description: ").strip()

    date = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip()

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions(type, category, amount, description, date)
    VALUES (?, ?, ?, ?, ?)
    """, (transaction_type, category, amount, description, date))

    conn.commit()
    conn.close()

    print(f"{transaction_type} added successfully!\n")


# ===========================================================
# VIEW TRANSACTIONS
# ===========================================================

def view_transactions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM transactions ORDER BY date DESC
    """)

    records = cursor.fetchall()

    conn.close()

    if not records:
        print("\nNo transactions found.\n")
        return

    print("\n================ TRANSACTIONS ================")
    print(f"{'ID':<5} {'TYPE':<10} {'CATEGORY':<15} {'AMOUNT':<10} {'DATE':<12} DESCRIPTION")
    print("-" * 80)

    for row in records:
        print(f"{row[0]:<5} {row[1]:<10} {row[2]:<15} {row[3]:<10.2f} {row[5]:<12} {row[4]}")

    print()


# ===========================================================
# MONTHLY SUMMARY
# ===========================================================

def monthly_summary():
    month = input("\nEnter month (YYYY-MM): ").strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT type, SUM(amount)
    FROM transactions
    WHERE date LIKE ?
    GROUP BY type
    """, (f"{month}%",))

    data = cursor.fetchall()

    conn.close()

    income = 0
    expense = 0

    for row in data:
        if row[0].lower() == "income":
            income = row[1]
        elif row[0].lower() == "expense":
            expense = row[1]

    balance = income - expense

    print("\n=========== MONTHLY SUMMARY ===========")
    print(f"Month   : {month}")
    print(f"Income  : {income:.2f}")
    print(f"Expense : {expense:.2f}")
    print(f"Balance : {balance:.2f}")
    print("=======================================\n")


# ===========================================================
# CATEGORY REPORT
# ===========================================================

def category_report():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM transactions
    WHERE type='Expense'
    GROUP BY category
    """)

    records = cursor.fetchall()

    conn.close()

    if not records:
        print("\nNo expense data found.\n")
        return

    print("\n======= CATEGORY-WISE EXPENSE REPORT =======")

    total = 0

    for category, amount in records:
        total += amount
        print(f"{category:<20}: {amount:.2f}")

    print("--------------------------------------------")
    print(f"Total Expense       : {total:.2f}")
    print("============================================\n")


# ===========================================================
# SEARCH TRANSACTIONS
# ===========================================================

def search_transactions():
    keyword = input("\nEnter keyword to search: ").strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM transactions
    WHERE category LIKE ?
    OR description LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    results = cursor.fetchall()

    conn.close()

    if not results:
        print("\nNo matching transactions found.\n")
        return

    print("\n=========== SEARCH RESULTS ===========")

    for row in results:
        print(row)

    print()


# ===========================================================
# DELETE TRANSACTION
# ===========================================================

def delete_transaction():
    view_transactions()

    try:
        transaction_id = int(input("Enter transaction ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM transactions
    WHERE id=?
    """, (transaction_id,))

    conn.commit()

    if cursor.rowcount > 0:
        print("Transaction deleted successfully!")
    else:
        print("Transaction ID not found.")

    conn.close()


# ===========================================================
# EXPORT TO CSV
# ===========================================================

def export_to_csv():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM transactions
    """)

    records = cursor.fetchall()

    conn.close()

    filename = "financial_report.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Type",
            "Category",
            "Amount",
            "Description",
            "Date"
        ])

        writer.writerows(records)

    print(f"\nData exported successfully to '{filename}'\n")


# ===========================================================
# BALANCE REPORT
# ===========================================================

def balance_report():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT type, SUM(amount)
    FROM transactions
    GROUP BY type
    """)

    data = cursor.fetchall()

    conn.close()

    income = 0
    expense = 0

    for row in data:
        if row[0].lower() == "income":
            income = row[1]
        elif row[0].lower() == "expense":
            expense = row[1]

    balance = income - expense

    print("\n============= OVERALL BALANCE =============")
    print(f"Total Income  : {income:.2f}")
    print(f"Total Expense : {expense:.2f}")
    print(f"Net Balance   : {balance:.2f}")
    print("===========================================\n")


# ===========================================================
# MAIN MENU
# ===========================================================

def menu():
    while True:
        print("""
================================================
        PERSONAL EXPENSE TRACKER
================================================
1. Add Income
2. Add Expense
3. View Transactions
4. Monthly Summary
5. Category-wise Expense Report
6. Search Transactions
7. Delete Transaction
8. Export Data to CSV
9. Overall Balance Report
0. Exit
================================================
        """)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_transaction("Income")

        elif choice == "2":
            add_transaction("Expense")

        elif choice == "3":
            view_transactions()

        elif choice == "4":
            monthly_summary()

        elif choice == "5":
            category_report()

        elif choice == "6":
            search_transactions()

        elif choice == "7":
            delete_transaction()

        elif choice == "8":
            export_to_csv()

        elif choice == "9":
            balance_report()

        elif choice == "0":
            print("\nThank you for using Personal Expense Tracker!")
            break

        else:
            print("\nInvalid choice. Please try again.\n")


# ===========================================================
# MAIN PROGRAM
# ===========================================================

if __name__ == "__main__":
    create_database()
    menu()