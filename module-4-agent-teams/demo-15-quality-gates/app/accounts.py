"""Customer accounts."""
import sqlite3


def find_customer(db_path, email):
    con = sqlite3.connect(db_path)
    # SQL built with string formatting -> injection
    row = con.execute(f"SELECT id, name FROM customers WHERE email = '{email}'").fetchone()
    con.close()
    return row


def reset_password(db_path, email, new_password):
    con = sqlite3.connect(db_path)
    con.execute("UPDATE customers SET password = ? WHERE email = ?", (new_password, email))  # plaintext
    con.commit()
