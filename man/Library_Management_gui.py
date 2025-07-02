import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# ---------- DATABASE ----------
conn = sqlite3.connect('library.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    quantity INTEGER
)''')

c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'admin')")
conn.commit()

# ---------- ROOT ----------
root = tk.Tk()
root.title("📚 Library Management System")
root.geometry("800x600")
root.config(bg="#f0f4ff")

# ---------- FRAMES ----------
home_frame = tk.Frame(root, bg="#f0f4ff")
login_frame = tk.Frame(root, bg="#f0f4ff")
admin_frame = tk.Frame(root, bg="#f0f4ff")  # Only shown after successful login

def show_frame(frame):
    for f in [home_frame, login_frame, admin_frame]:
        f.pack_forget()
    frame.pack(fill="both", expand=True)

# ---------- HOME ----------
def load_home():
    book_tree_home.delete(*book_tree_home.get_children())
    for row in c.execute("SELECT title, author, quantity FROM books"):
        book_tree_home.insert("", tk.END, values=row)

tk.Label(home_frame, text="📚 Welcome to the Library", font=("Arial", 22, "bold"), bg="#f0f4ff").pack(pady=10)

book_tree_home = ttk.Treeview(home_frame, columns=("Title", "Author", "Qty"), show="headings")
for col in ("Title", "Author", "Qty"):
    book_tree_home.heading(col, text=col)
    book_tree_home.column(col, width=200)
book_tree_home.pack(pady=20)

# Top bar for Admin Login
top_bar = tk.Frame(home_frame, bg="#f0f4ff")
top_bar.pack(fill="x", anchor="n")

admin_btn = tk.Button(top_bar, text="🔐 Admin Login", bg="#0077cc", fg="white",
                      font=("Arial", 10, "bold"), padx=10, pady=2,
                      command=lambda: show_frame(login_frame))
admin_btn.pack(side="right", padx=10, pady=10)


# ---------- LOGIN ----------
def login():
    user = username_entry.get().strip()
    pw = password_entry.get().strip()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
    if c.fetchone():
        show_frame(admin_frame)
        refresh_admin_books()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

tk.Label(login_frame, text="Admin Login", font=("Arial", 20, "bold"), bg="#f0f4ff").pack(pady=20)

tk.Label(login_frame, text="Username", bg="#f0f4ff").pack()
username_entry = tk.Entry(login_frame)
username_entry.pack(pady=5)

tk.Label(login_frame, text="Password", bg="#f0f4ff").pack()
password_entry = tk.Entry(login_frame, show="*")
password_entry.pack(pady=5)

tk.Button(login_frame, text="Login", bg="#28a745", fg="white", font=("Arial", 10, "bold"), command=login).pack(pady=15)
tk.Button(login_frame, text="⬅ Back", command=lambda: show_frame(home_frame)).pack()

# ---------- ADMIN DASHBOARD ----------
def add_book():
    title = title_entry.get()
    author = author_entry.get()
    qty = qty_entry.get()

    if not title or not author or not qty:
        messagebox.showwarning("Input error", "All fields are required.")
        return

    try:
        qty = int(qty)
        c.execute("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)", (title, author, qty))
        conn.commit()
        refresh_admin_books()
        clear_book_fields()
    except:
        messagebox.showerror("Error", "Quantity must be a number.")

def delete_book():
    selected = book_tree_admin.selection()
    if selected:
        # Get the title and author of the selected book
        selected_item = book_tree_admin.item(selected[0])
        title = selected_item['values'][1]
        author = selected_item['values'][2]


        # Get the actual book_id from the database using the title and author
        c.execute("SELECT book_id FROM books WHERE title=? AND author=?", (title, author))
        result = c.fetchone()
        
        if result:
            book_id = result[0]
            # Delete the book from the database using the book_id
            c.execute("DELETE FROM books WHERE book_id=?", (book_id,))
            conn.commit()
            # Refresh the book list to update the index and remove the deleted book
            refresh_admin_books()
        else:
            messagebox.showerror("Error", "Book not found.")
    else:
        messagebox.showinfo("Select", "Please select a book to delete.")


def refresh_admin_books():
    book_tree_admin.delete(*book_tree_admin.get_children())
    rows = c.execute("SELECT * FROM books").fetchall()
    for i, row in enumerate(rows, start=1):
        book_tree_admin.insert("", tk.END, values=(i, row[1], row[2], row[3]))
    load_home()

def clear_book_fields():
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)

tk.Label(admin_frame, text="📖 Admin Dashboard", font=("Arial", 20, "bold"), bg="#f0f4ff").pack(pady=10)

form_frame = tk.Frame(admin_frame, bg="#f0f4ff")
form_frame.pack(pady=5)

tk.Label(form_frame, text="Title", bg="#f0f4ff").grid(row=0, column=0)
title_entry = tk.Entry(form_frame)
title_entry.grid(row=0, column=1)

tk.Label(form_frame, text="Author", bg="#f0f4ff").grid(row=0, column=2)
author_entry = tk.Entry(form_frame)
author_entry.grid(row=0, column=3)

tk.Label(form_frame, text="Quantity", bg="#f0f4ff").grid(row=0, column=4)
qty_entry = tk.Entry(form_frame)
qty_entry.grid(row=0, column=5)

tk.Button(form_frame, text="Add Book", bg="#1e88e5", fg="white", command=add_book).grid(row=0, column=6, padx=5)

book_tree_admin = ttk.Treeview(admin_frame, columns=("ID", "Title", "Author", "Qty"), show="headings")
for col in ("ID", "Title", "Author", "Qty"):
    book_tree_admin.heading(col, text=col)
    book_tree_admin.column(col, width=150)
book_tree_admin.pack(pady=20)

tk.Button(admin_frame, text="🗑 Delete Book", bg="#e53935", fg="white", command=delete_book).pack()
tk.Button(admin_frame, text="⬅ Logout to Home", command=lambda: show_frame(home_frame)).pack(pady=10)

# ---------- START ----------
show_frame(home_frame)
load_home()
root.mainloop()
