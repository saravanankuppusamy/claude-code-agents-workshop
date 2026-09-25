#!/usr/bin/env python3
"""Create (or reset) db/tidewater.db for the hooks demo.   python3 setup_db.py

Deliberate traps for naive keyword guards:
  - books.drop_date column          -> naive 'DROP' substring match false positive
  - a book titled 'Delete Me Not'   -> naive 'DELETE' match inside a string literal
  - staff_payroll table             -> sensitive; must be blocked by the table allowlist
"""
import os
import random
import sqlite3

random.seed(7)
os.makedirs("db", exist_ok=True)
path = "db/tidewater.db"
if os.path.exists(path):
    os.remove(path)
con = sqlite3.connect(path)
cur = con.cursor()
cur.executescript("""
CREATE TABLE books (isbn TEXT PRIMARY KEY, title TEXT, author TEXT, price REAL,
                    stock INTEGER, drop_date TEXT);
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, city TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, isbn TEXT,
                     qty INTEGER, ordered_at TEXT, status TEXT);
CREATE TABLE staff_payroll (staff_id INTEGER PRIMARY KEY, name TEXT, salary INTEGER,
                            bank_sort_code TEXT);
""")
titles = ["The Tide Clock", "Salt and Cedar", "Delete Me Not: A Memoir", "North of the Harbour",
          "A Field Guide to Gulls", "The Quiet Ledger", "Knots for Beginners", "Moonrise at Low Water",
          "Paper Boats", "The Lighthouse Accounts", "Kelp Forest Recipes", "Drop Anchor"]
authors = ["M. Fenwick", "A. Osei", "R. Castellano", "J. Nakamura", "P. Lindqvist"]
for i, t in enumerate(titles):
    cur.execute("INSERT INTO books VALUES (?,?,?,?,?,?)",
                (f"97800000{i:05d}", t, random.choice(authors), round(random.uniform(6, 140), 2),
                 random.randint(0, 40), "2026-12-31" if i % 4 == 0 else None))
cities = ["Leith", "Whitby", "Falmouth", "Oban", "Tenby"]
for c in range(1, 41):
    cur.execute("INSERT INTO customers VALUES (?,?,?,?)",
                (c, f"Customer {c}", f"c{c}@example.com", random.choice(cities)))
for o in range(1, 301):
    cur.execute("INSERT INTO orders VALUES (?,?,?,?,?,?)",
                (o, random.randint(1, 40), f"97800000{random.randint(0, len(titles)-1):05d}",
                 random.randint(1, 3), f"2026-0{random.randint(6, 9)}-{random.randint(10, 28)}",
                 random.choice(["shipped", "shipped", "pending", "cancelled"])))
for s in range(1, 9):
    cur.execute("INSERT INTO staff_payroll VALUES (?,?,?,?)",
                (s, f"Staff {s}", random.randint(24000, 61000), f"{random.randint(10,99)}-00-00"))
con.commit()
con.close()
print(f"created {path}: books(12) customers(40) orders(300) staff_payroll(8)")
