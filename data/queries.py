import sqlite3

from data import database


# users

def count_users():
    rows = database.run_query("SELECT COUNT(*) AS total FROM users")
    return rows[0]["total"]
