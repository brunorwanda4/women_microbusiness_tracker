import sqlite3

from data import database


# users

def count_users():
    rows = database.run_query("SELECT COUNT(*) AS total FROM users")
    return rows[0]["total"]

# products

def add_product(name, cost_price, selling_price, stock):
    cursor = database.run_change(
        "INSERT INTO products (name, cost_price, selling_price, stock) VALUES (?, ?, ?, ?)",
        (name, cost_price, selling_price, stock),
    )
    return cursor.lastrowid


def get_all_products():
    return database.run_query("SELECT * FROM products ORDER BY name")


def get_product_by_id(product_id):
    rows = database.run_query("SELECT * FROM products WHERE id = ?", (product_id,))
    if len(rows) == 0:
        return None
    return rows[0]


def get_product_by_name(name):
    rows = database.run_query("SELECT * FROM products WHERE name = ?", (name,))
    if len(rows) == 0:
        return None
    return rows[0]


def search_products(text):
    return database.run_query(
        "SELECT * FROM products WHERE name LIKE ? ORDER BY name",
        ("%" + text + "%",),
    )


def update_product(product_id, name, cost_price, selling_price, stock):
    database.run_change(
        "UPDATE products SET name = ?, cost_price = ?, selling_price = ?, stock = ? WHERE id = ?",
        (name, cost_price, selling_price, stock, product_id),
    )


def add_stock(product_id, quantity):
    database.run_change(
        "UPDATE products SET stock = stock + ? WHERE id = ?",
        (quantity, product_id),
    )


def delete_product(product_id):
    database.run_change("DELETE FROM products WHERE id = ?", (product_id,))


def get_total_stock():
    rows = database.run_query("SELECT COALESCE(SUM(stock), 0) AS total FROM products")
    return rows[0]["total"]

# sales

def add_sale(product_id, quantity, cost_price, selling_price, sale_date, user_id):
    # two steps that must both work: lower the stock and save the sale
    connection = database.connection
    try:
        cursor = connection.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
            (quantity, product_id, quantity),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            raise ValueError("Not enough stock for this sale.")
        cursor = connection.execute(
            "INSERT INTO sales (product_id, quantity, cost_price, selling_price, sale_date, user_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (product_id, quantity, cost_price, selling_price, sale_date, user_id),
        )
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        connection.rollback()
        raise ValueError("Could not save the sale. Please try again.")


def cancel_sale(sale_id):
    # put the stock back and remove the sale
    connection = database.connection
    try:
        sale = connection.execute(
            "SELECT product_id, quantity FROM sales WHERE id = ?", (sale_id,)
        ).fetchone()
        if sale is None:
            raise ValueError("That sale was not found.")
        connection.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (sale["quantity"], sale["product_id"]),
        )
        connection.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        raise ValueError("Could not cancel the sale. Please try again.")


def get_all_sales():
    return database.run_query(
        "SELECT sales.id, sales.sale_date, products.name AS product, sales.quantity, "
        "sales.selling_price, sales.quantity * sales.selling_price AS total, "
        "users.name AS sold_by "
        "FROM sales "
        "JOIN products ON sales.product_id = products.id "
        "LEFT JOIN users ON sales.user_id = users.id "
        "ORDER BY sales.sale_date DESC, sales.id DESC"
    )


def get_sale_by_id(sale_id):
    rows = database.run_query("SELECT * FROM sales WHERE id = ?", (sale_id,))
    if len(rows) == 0:
        return None
    return rows[0]


def count_sales_for_product(product_id):
    rows = database.run_query(
        "SELECT COUNT(*) AS total FROM sales WHERE product_id = ?", (product_id,)
    )
    return rows[0]["total"]


# dates are saved as text like 2026-10-28, so BETWEEN works on them
def get_sale_totals(start_date, end_date):
    rows = database.run_query(
        "SELECT COALESCE(SUM(quantity * selling_price), 0) AS revenue, "
        "COALESCE(SUM(quantity * cost_price), 0) AS cogs, "
        "COALESCE(SUM(quantity), 0) AS units "
        "FROM sales WHERE sale_date BETWEEN ? AND ?",
        (start_date, end_date),
    )
    return rows[0]


def get_sale_totals_by_product(start_date, end_date):
    return database.run_query(
        "SELECT products.name AS product, SUM(sales.quantity) AS units, "
        "SUM(sales.quantity * sales.selling_price) AS revenue, "
        "SUM(sales.quantity * sales.cost_price) AS cogs "
        "FROM sales JOIN products ON sales.product_id = products.id "
        "WHERE sales.sale_date BETWEEN ? AND ? "
        "GROUP BY products.id",
        (start_date, end_date),
    )


# expenses

def add_expense(description, amount, expense_date, user_id):
    cursor = database.run_change(
        "INSERT INTO expenses (description, amount, expense_date, user_id) VALUES (?, ?, ?, ?)",
        (description, amount, expense_date, user_id),
    )
    return cursor.lastrowid


def get_all_expenses():
    return database.run_query(
        "SELECT expenses.id, expenses.expense_date, expenses.description, expenses.amount, "
        "users.name AS added_by "
        "FROM expenses LEFT JOIN users ON expenses.user_id = users.id "
        "ORDER BY expenses.expense_date DESC, expenses.id DESC"
    )


def get_expense_by_id(expense_id):
    rows = database.run_query("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    if len(rows) == 0:
        return None
    return rows[0]


def update_expense(expense_id, description, amount, expense_date):
    database.run_change(
        "UPDATE expenses SET description = ?, amount = ?, expense_date = ? WHERE id = ?",
        (description, amount, expense_date, expense_id),
    )


def delete_expense(expense_id):
    database.run_change("DELETE FROM expenses WHERE id = ?", (expense_id,))


def get_expense_total(start_date, end_date):
    rows = database.run_query(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses "
        "WHERE expense_date BETWEEN ? AND ?",
        (start_date, end_date),
    )
    return rows[0]["total"]
