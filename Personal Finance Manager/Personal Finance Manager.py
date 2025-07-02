import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# ---------- DATABASE ----------
conn = sqlite3.connect("finance.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    amount REAL,
    category TEXT,
    note TEXT,
    date TEXT
)''')
conn.commit()


# ---------- FUNCTIONS ----------
def add_transaction():
    t_type = type_var.get()
    amount = amount_entry.get()
    category = category_entry.get()
    note = note_entry.get()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not amount.strip():
        messagebox.showerror("Error", "Amount is required")
        return

    try:
        amt = float(amount)
        cursor.execute("INSERT INTO transactions (type, amount, category, note, date) VALUES (?, ?, ?, ?, ?)",
                       (t_type, amt, category, note, date))
        conn.commit()
        messagebox.showinfo("Success", f"{t_type} added.")
        refresh_table()
        clear_fields()
    except:
        messagebox.showerror("Error", "Enter a valid number for amount")

def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    balance = 0
    for row in cursor.fetchall():
        tid, ttype, amount, cat, note, date = row
        balance += amount if ttype == "Income" else -amount
        tree.insert('', tk.END, values=(ttype, f"₹{amount:.2f}", cat, note, date))
    balance_label.config(text=f"💰 Current Balance: ₹{balance:.2f}")

def clear_fields():
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    note_entry.delete(0, tk.END)

# ---------- GUI ----------
root = tk.Tk()
root.title("💼 Personal Finance Manager")
root.geometry("700x600")
root.config(bg="#f8f9fa")

tk.Label(root, text="Add Transaction", bg="#f8f9fa", fg="#343a40", font=("Arial", 16, "bold")).pack(pady=10)

form_frame = tk.Frame(root, bg="#f8f9fa")
form_frame.pack(pady=10)

# Type
tk.Label(form_frame, text="Type", bg="#f8f9fa").grid(row=0, column=0)
type_var = tk.StringVar(value="Income")
ttk.Combobox(form_frame, textvariable=type_var, values=["Income", "Expense"], state="readonly").grid(row=1, column=0, padx=10)

# Amount
tk.Label(form_frame, text="Amount", bg="#f8f9fa").grid(row=0, column=1)
amount_entry = tk.Entry(form_frame)
amount_entry.grid(row=1, column=1, padx=10)

# Category
tk.Label(form_frame, text="Category", bg="#f8f9fa").grid(row=0, column=2)
category_entry = tk.Entry(form_frame)
category_entry.grid(row=1, column=2, padx=10)

# Note
tk.Label(form_frame, text="Note", bg="#f8f9fa").grid(row=0, column=3)
note_entry = tk.Entry(form_frame)
note_entry.grid(row=1, column=3, padx=10)

# Buttons
tk.Button(root, text="Add", bg="#198754", fg="white", font=("Arial", 10, "bold"),
          command=add_transaction).pack(pady=5)

# TreeView
columns = ("Type", "Amount", "Category", "Note", "Date")
tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(pady=10)

# Balance
balance_label = tk.Label(root, text="💰 Current Balance: ₹0.00", bg="#f8f9fa", fg="#212529", font=("Arial", 14, "bold"))
balance_label.pack(pady=10)

refresh_table()
root.mainloop()
