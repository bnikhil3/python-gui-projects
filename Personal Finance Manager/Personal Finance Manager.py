import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# -------------------- Database Setup --------------------
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL
)''')
conn.commit()

# -------------------- Functions --------------------
def add_transaction():
    t_type = type_var.get()
    category = category_entry.get()
    amount = amount_entry.get()

    if not category or not amount:
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Invalid Input", "Amount must be a number.")
        return

    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO transactions (type, category, amount, date) VALUES (?, ?, ?, ?)",
                   (t_type, category, amount, date))
    conn.commit()
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    refresh_transactions()
    update_balance()

def refresh_transactions():
    for row in transaction_tree.get_children():
        transaction_tree.delete(row)
    cursor.execute("SELECT type, category, amount, date FROM transactions ORDER BY date DESC")
    for row in cursor.fetchall():
        transaction_tree.insert("", tk.END, values=row)

def update_balance():
    cursor.execute("SELECT type, amount FROM transactions")
    income = sum(row[1] for row in cursor.fetchall() if row[0] == "Income")
    cursor.execute("SELECT type, amount FROM transactions")
    expense = sum(row[1] for row in cursor.fetchall() if row[0] == "Expense")
    balance = income - expense
    balance_var.set(f"Balance: ₹{balance:.2f}  |  Income: ₹{income:.2f}  |  Expense: ₹{expense:.2f}")

def show_monthly_summary():
    now = datetime.now()
    this_month = now.strftime("%Y-%m")
    cursor.execute("SELECT type, amount, date FROM transactions WHERE strftime('%Y-%m', date) = ?", (this_month,))
    totals = defaultdict(float)
    for ttype, amount, _ in cursor.fetchall():
        totals[ttype] += amount if ttype == "Income" else -amount

    income = totals.get("Income", 0)
    expense = abs(totals.get("Expense", 0))

    fig, ax = plt.subplots()
    ax.bar(["Income", "Expense"], [income, expense], color=["green", "red"])
    ax.set_title(f"Monthly Summary - {this_month}")
    ax.set_ylabel("Amount (₹)")
    plt.tight_layout()
    plt.show()

def show_expense_pie_chart():
    now = datetime.now()
    this_month = now.strftime("%Y-%m")
    cursor.execute("SELECT category, amount FROM transactions WHERE type='Expense' AND strftime('%Y-%m', date) = ?", (this_month,))
    data = cursor.fetchall()
    category_totals = defaultdict(float)

    for category, amount in data:
        category_totals[category] += amount

    if category_totals:
        labels = list(category_totals.keys())
        sizes = list(category_totals.values())

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.title(f"Expense Breakdown - {this_month}")
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showinfo("No Data", "No expense data available for this month.")

# -------------------- GUI Setup --------------------
root = tk.Tk()
root.title("💸 Personal Finance Manager")
root.geometry("700x600")
root.config(bg="#f7faff")

# Title
tk.Label(root, text="📊 Personal Finance Dashboard", font=("Arial", 20, "bold"), bg="#f7faff").pack(pady=10)

# Balance Label
balance_var = tk.StringVar()
balance_label = tk.Label(root, textvariable=balance_var, font=("Arial", 14), bg="#f7faff", fg="#0d6efd")
balance_label.pack(pady=10)

# Show Graph Buttons
tk.Button(root, text="📈 Show Monthly Summary", bg="#0d6efd", fg="white",
          font=("Arial", 10, "bold"), command=show_monthly_summary).pack(pady=5)

tk.Button(root, text="🥧 Expense Breakdown (Pie Chart)", bg="#6c63ff", fg="white",
          font=("Arial", 10, "bold"), command=show_expense_pie_chart).pack(pady=5)

# Transaction Entry Frame
entry_frame = tk.Frame(root, bg="#f7faff")
entry_frame.pack(pady=10)

type_var = tk.StringVar(value="Expense")
tk.OptionMenu(entry_frame, type_var, "Income", "Expense").grid(row=0, column=0, padx=10)
category_entry = tk.Entry(entry_frame, width=20)
category_entry.grid(row=0, column=1, padx=10)
category_entry.insert(0, "Category")

amount_entry = tk.Entry(entry_frame, width=15)
amount_entry.grid(row=0, column=2, padx=10)
amount_entry.insert(0, "Amount")

tk.Button(entry_frame, text="Add Transaction", bg="#28a745", fg="white",
          command=add_transaction).grid(row=0, column=3, padx=10)

# Transactions Table
columns = ("Type", "Category", "Amount", "Date")
transaction_tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    transaction_tree.heading(col, text=col)
    transaction_tree.column(col, width=150)
transaction_tree.pack(pady=20)

# Initialize
refresh_transactions()
update_balance()

root.mainloop()
