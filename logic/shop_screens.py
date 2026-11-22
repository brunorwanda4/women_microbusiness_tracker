from frontend import inputs
from logic import checks, shop_logic, user_logic


# products

def show_products(products):
    if len(products) == 0:
        print("No products to show.")
        return
    print(f"{'No.':<5}{'Product':<26}{'Cost':>10}{'Price':>10}{'Stock':>8}")
    print("-" * 59)
    for product in products:
        note = ""
        if product["stock"] <= shop_logic.LOW_STOCK:
            note = "  LOW"
        print(f"{product['id']:<5}{product['name']:<26}{product['cost_price']:>10,}"
              f"{product['selling_price']:>10,}{product['stock']:>8}{note}")


def product_menu(user):
    while True:
        print("\n--- Products ---")
        print("1. Add a product")
        print("2. View all products")
        print("3. Search products by name")
        print("4. Update a product")
        print("5. Add stock")
        print("6. Delete a product")
        print("0. Back")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                add_product(user)
            elif choice == "2":
                show_products(shop_logic.get_products(user))
            elif choice == "3":
                search_products(user)
            elif choice == "4":
                update_product(user)
            elif choice == "5":
                add_stock(user)
            elif choice == "6":
                delete_product(user)
            elif choice == "0":
                break
            else:
                print("Please choose a number from the menu.")
        except ValueError as error:
            print(error)


def add_product(user):
    name = inputs.ask("Product name: ", checks.check_name)
    cost_price = inputs.ask("Cost price (RWF): ", checks.check_whole_number)
    selling_price = inputs.ask("Selling price (RWF): ", checks.check_positive_number)
    stock = inputs.ask("Stock quantity: ", checks.check_whole_number)

    if selling_price < cost_price:
        print("Warning: the selling price is lower than the cost price.")
        if not inputs.ask_yes("Save anyway?"):
            print("Product not saved.")
            return

    shop_logic.add_product(user, name, cost_price, selling_price, stock)
    print(f"Saved: {stock} x {name} (cost {cost_price:,} RWF, price {selling_price:,} RWF).")


def search_products(user):
    text = inputs.ask("Search for: ", checks.check_name)
    show_products(shop_logic.search_products(user, text))


def update_product(user):
    show_products(shop_logic.get_products(user))
    product_id = inputs.ask("Product number to update: ", checks.check_positive_number)
    product = shop_logic.get_product(user, product_id)

    print("Press Enter to keep the current value.")
    name = inputs.ask(f"Product name [{product['name']}]: ", checks.check_name, product["name"])
    cost_price = inputs.ask(f"Cost price [{product['cost_price']}]: ",
                            checks.check_whole_number, product["cost_price"])
    selling_price = inputs.ask(f"Selling price [{product['selling_price']}]: ",
                               checks.check_positive_number, product["selling_price"])
    stock = inputs.ask(f"Stock [{product['stock']}]: ", checks.check_whole_number, product["stock"])

    shop_logic.update_product(user, product_id, name, cost_price, selling_price, stock)
    print("Product updated.")


def add_stock(user):
    show_products(shop_logic.get_products(user))
    product_id = inputs.ask("Product number: ", checks.check_positive_number)
    quantity = inputs.ask("How many items to add: ", checks.check_positive_number)
    new_stock = shop_logic.add_stock(user, product_id, quantity)
    print(f"Stock updated. There are now {new_stock} in stock.")


def delete_product(user):
    show_products(shop_logic.get_products(user))
    product_id = inputs.ask("Product number to delete: ", checks.check_positive_number)
    product = shop_logic.get_product(user, product_id)
    if inputs.ask_yes(f"Delete {product['name']}?"):
        shop_logic.delete_product(user, product_id)
        print("Product deleted.")
    else:
        print("Nothing was deleted.")


# sales

def show_sales(sales):
    if len(sales) == 0:
        print("No sales yet.")
        return
    print(f"{'No.':<5}{'Date':<12}{'Product':<26}{'Qty':>5}{'Total':>12}  Sold by")
    print("-" * 70)
    for sale in sales:
        sold_by = sale["sold_by"]
        if sold_by is None:
            sold_by = "(deleted user)"
        print(f"{sale['id']:<5}{sale['sale_date']:<12}{sale['product']:<26}"
              f"{sale['quantity']:>5}{sale['total']:>12,}  {sold_by}")
    total = sum([sale["total"] for sale in sales])
    print("-" * 70)
    print(f"Total of all sales: {total:,} RWF")


def sales_menu(user):
    while True:
        print("\n--- Sales ---")
        print("1. Record a sale")
        if user_logic.has_permission(user, "view_sales"):
            print("2. View all sales")
        if user_logic.has_permission(user, "cancel_sale"):
            print("3. Cancel a sale")
        print("0. Back")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                record_sale(user)
            elif choice == "2":
                show_sales(shop_logic.get_sales(user))
            elif choice == "3":
                cancel_sale(user)
            elif choice == "0":
                break
            else:
                print("Please choose a number from the menu.")
        except ValueError as error:
            print(error)


def record_sale(user):
    products = shop_logic.get_products(user)
    show_products(products)
    if len(products) == 0:
        return

    product_id = inputs.ask("Product number: ", checks.check_positive_number)
    quantity = inputs.ask("Quantity sold: ", checks.check_positive_number)
    if user_logic.has_permission(user, "choose_date"):
        sale_date = inputs.ask("Date (YYYY-MM-DD, Enter for today): ",
                               checks.check_date, checks.today())
    else:
        sale_date = checks.today()

    result = shop_logic.record_sale(user, product_id, quantity, sale_date)
    print(f"Sale recorded: {quantity} x {result['name']} = {result['total']:,} RWF. "
          f"Stock left: {result['stock_left']}.")


def cancel_sale(user):
    show_sales(shop_logic.get_sales(user))
    sale_id = inputs.ask("Sale number to cancel: ", checks.check_positive_number)
    if inputs.ask_yes(f"Cancel sale {sale_id}? The stock will be put back."):
        shop_logic.cancel_sale(user, sale_id)
        print("Sale cancelled and stock put back.")
    else:
        print("Nothing was cancelled.")


# expenses

def show_expenses(expenses):
    if len(expenses) == 0:
        print("No expenses yet.")
        return
    print(f"{'No.':<5}{'Date':<12}{'What for':<42}{'Amount':>10}  Added by")
    print("-" * 77)
    for expense in expenses:
        added_by = expense["added_by"]
        if added_by is None:
            added_by = "(deleted user)"
        print(f"{expense['id']:<5}{expense['expense_date']:<12}{expense['description']:<42}"
              f"{expense['amount']:>10,}  {added_by}")
    total = sum([expense["amount"] for expense in expenses])
    print("-" * 77)
    print(f"Total expenses: {total:,} RWF")


def expenses_menu(user):
    while True:
        print("\n--- Expenses ---")
        print("1. Record an expense")
        print("2. View all expenses")
        print("3. Edit an expense")
        print("4. Delete an expense")
        print("0. Back")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                add_expense(user)
            elif choice == "2":
                show_expenses(shop_logic.get_expenses(user))
            elif choice == "3":
                edit_expense(user)
            elif choice == "4":
                delete_expense(user)
            elif choice == "0":
                break
            else:
                print("Please choose a number from the menu.")
        except ValueError as error:
            print(error)


def add_expense(user):
    description = inputs.ask("What was it for (for example transport): ", checks.check_description)
    amount = inputs.ask("Amount (RWF): ", checks.check_positive_number)
    expense_date = inputs.ask("Date (YYYY-MM-DD, Enter for today): ",
                              checks.check_date, checks.today())
    shop_logic.add_expense(user, description, amount, expense_date)
    print(f"Expense recorded: {description}, {amount:,} RWF.")


def edit_expense(user):
    show_expenses(shop_logic.get_expenses(user))
    expense_id = inputs.ask("Expense number to edit: ", checks.check_positive_number)
    expense = shop_logic.get_expense(user, expense_id)

    print("Press Enter to keep the current value.")
    description = inputs.ask(f"What was it for [{expense['description']}]: ",
                             checks.check_description, expense["description"])
    amount = inputs.ask(f"Amount [{expense['amount']}]: ",
                        checks.check_positive_number, expense["amount"])
    expense_date = inputs.ask(f"Date [{expense['expense_date']}]: ",
                              checks.check_date, expense["expense_date"])

    shop_logic.update_expense(user, expense_id, description, amount, expense_date)
    print("Expense updated.")


def delete_expense(user):
    show_expenses(shop_logic.get_expenses(user))
    expense_id = inputs.ask("Expense number to delete: ", checks.check_positive_number)
    expense = shop_logic.get_expense(user, expense_id)
    if inputs.ask_yes(f"Delete '{expense['description']}' ({expense['amount']:,} RWF)?"):
        shop_logic.delete_expense(user, expense_id)
        print("Expense deleted.")
    else:
        print("Nothing was deleted.")


