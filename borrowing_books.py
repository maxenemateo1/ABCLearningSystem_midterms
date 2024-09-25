import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pyodbc  # Ensure pyodbc is installed and imported
from database import connect_to_db  # Ensure this function is correctly defined

def open_borrowing_books_window(parent, username):
    """Open a new window for borrowing books."""
    borrowing_window = tk.Toplevel(parent)
    borrowing_window.title("Borrowing Books")
    borrowing_window.geometry("800x600")  # Adjust size as needed

    setup_transactions_interface(borrowing_window, username)

def setup_transactions_interface(tab, username):
    """Setup the transactions interface with main tab control and nested sub-tab controls."""
    # Header
    header_frame = tk.Frame(tab, bg="#C39898")
    header_frame.pack(fill=tk.X, pady=5)

    tk.Label(header_frame, text="ABC LEARNING RESOURCE CENTER", font=("Arial", 16, "bold"), bg="#C39898").pack(side=tk.LEFT, padx=10)
    tk.Label(header_frame, text=f"Welcome, {username}!", font=("Arial", 14), bg="#C39898").pack(side=tk.RIGHT, padx=10)

    # Main Tab Control
    main_tab_control = ttk.Notebook(tab)
    main_tab_control.pack(fill=tk.BOTH, expand=True)

    # Borrow Transaction Tab
    borrow_transaction_tab = ttk.Frame(main_tab_control)
    main_tab_control.add(borrow_transaction_tab, text="Borrow Transaction")

    # Return Transaction Tab
    return_transaction_tab = ttk.Frame(main_tab_control)
    main_tab_control.add(return_transaction_tab, text="Return Transaction")

    # Administrative Transactions Tab
    administrative_tab = ttk.Frame(main_tab_control)
    main_tab_control.add(administrative_tab, text="Administrative Transactions")

    # Setup Tabs
    setup_borrow_transaction_tabs(borrow_transaction_tab, username)
    setup_return_transaction_interface(return_transaction_tab)
    setup_administrative_transactions_interface(administrative_tab)

def setup_borrow_transaction_tabs(tab, username):
    """Setup the Borrow Transaction tab with nested sub-tabs for 'Manual Entry' and 'Reservation'."""
    # Sub-tab Control for Borrow Transaction
    borrow_transaction_notebook = ttk.Notebook(tab)
    borrow_transaction_notebook.pack(fill=tk.BOTH, expand=True)

    # Manual Entry Sub-tab
    manual_entry_frame = ttk.Frame(borrow_transaction_notebook)
    borrow_transaction_notebook.add(manual_entry_frame, text="Manual Entry")

    # Reservation Sub-tab
    reservation_frame = ttk.Frame(borrow_transaction_notebook)
    borrow_transaction_notebook.add(reservation_frame, text="Reservation")

    # Setup Sub-tabs
    setup_manual_entry_interface(manual_entry_frame, username)
    setup_reservation_interface(reservation_frame, username)

def setup_manual_entry_interface(tab, username):
    """Setup the Manual Entry sub-tab interface with required functionalities, filter, and cart grid."""
    global cart_tree  # Declare cart_tree as global

    # Book Information Frame
    book_info_frame = tk.Frame(tab, relief=tk.RIDGE, borderwidth=2)
    book_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Label(book_info_frame, text="Book Information", font=("Arial", 12, "bold")).pack(pady=5)

    tk.Label(book_info_frame, text="Available", anchor="w").pack(anchor="w", padx=10, pady=5)
    tk.Label(book_info_frame, text="ISBN", anchor="w").pack(anchor="w", padx=10, pady=5)
    tk.Label(book_info_frame, text="Title", anchor="w").pack(anchor="w", padx=10, pady=5)
    tk.Label(book_info_frame, text="Author", anchor="w").pack(anchor="w", padx=10, pady=5)
    tk.Label(book_info_frame, text="Abstract", anchor="w").pack(anchor="w", padx=10, pady=5)

    # Book Information Values
    available_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    isbn_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    title_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    author_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    abstract_text = tk.Text(book_info_frame, height=5, width=30, wrap="word", relief=tk.SUNKEN)

    available_label.pack(padx=10, pady=5, anchor="w")
    isbn_label.pack(padx=10, pady=5, anchor="w")
    title_label.pack(padx=10, pady=5, anchor="w")
    author_label.pack(padx=10, pady=5, anchor="w")
    abstract_text.pack(padx=10, pady=5, anchor="w")

    # Navigation Buttons
    nav_frame = tk.Frame(book_info_frame)
    nav_frame.pack(pady=10)

    tk.Button(nav_frame, text="<<", relief=tk.GROOVE, width=3).pack(side="left", padx=5)
    tk.Button(nav_frame, text=">>", relief=tk.GROOVE, width=3).pack(side="left", padx=5)

    # Filter Section
    filter_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    filter_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Label(filter_frame, text="Filter Books", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    tk.Label(filter_frame, text="Category").pack(anchor="w", padx=10)
    category_entry = tk.Entry(filter_frame)
    category_entry.pack(anchor="w", padx=10, pady=5)

    tk.Label(filter_frame, text="Title").pack(anchor="w", padx=10)
    title_entry = tk.Entry(filter_frame)
    title_entry.pack(anchor="w", padx=10, pady=5)

    tk.Label(filter_frame, text="Author").pack(anchor="w", padx=10)
    author_entry = tk.Entry(filter_frame)
    author_entry.pack(anchor="w", padx=10, pady=5)

    tk.Label(filter_frame, text="ISBN").pack(anchor="w", padx=10)
    isbn_entry = tk.Entry(filter_frame)
    isbn_entry.pack(anchor="w", padx=10, pady=5)

    # Search Button
    tk.Button(filter_frame, text="Search", relief=tk.GROOVE, command=lambda: search_books(
        category_entry.get(), title_entry.get(), author_entry.get(), isbn_entry.get())).pack(pady=10, padx=10)

    # Cart Section
    cart_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    cart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Label(cart_frame, text="Cart", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Cart Table
    cart_tree = ttk.Treeview(cart_frame, columns=("title", "isbn"), show="headings", selectmode="extended")
    cart_tree.heading("title", text="Title")
    cart_tree.heading("isbn", text="ISBN")
    cart_tree.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Cart Buttons
    button_frame = tk.Frame(cart_frame)
    button_frame.pack(side="right", fill=tk.Y, padx=10, pady=10)

    tk.Button(button_frame, text="Remove Selected Book", relief=tk.GROOVE, command=lambda: remove_cart_item(cart_tree)).pack(side="top", padx=5, pady=5)
    tk.Button(button_frame, text="Reserve Listed Books", relief=tk.GROOVE, command=lambda: reserve_cart_items(cart_tree, username)).pack(side="top", padx=5, pady=5)

def search_transactions(user_id, isbn):
    """Function to search transactions based on UserID and ISBN."""
    try:
        connection = connect_to_db()  # Use your connection function
        if connection is None:
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            return

        cursor = connection.cursor()

        # SQL query to fetch transaction records
        query = """
        SELECT ISBN, DateBorrowed, IsBookReturned
        FROM tblBorrowTran
        WHERE UserID = ? AND (ISBN = ? OR ? = '')
        """

        cursor.execute(query, (user_id, isbn, isbn))
        rows = cursor.fetchall()

        # Populate the Treeview with results (assuming you have a Treeview defined)
        for row in rows:
            transaction_tree.insert("", tk.END, values=row)  # Ensure transaction_tree is defined

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Database Error", f"An error occurred: {e}")

    finally:
        if connection:
            connection.close()

def search_books(category, title, author, isbn):
    """Function to search books based on filter criteria and update the UI."""
    # Clear the existing items in the Treeview
    for item in cart_tree.get_children():
        cart_tree.delete(item)

    # Connect to your database
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Construct the SQL query with filter conditions
        query = """
        SELECT Title, ISBN
        FROM tblBooks
        WHERE (Category = ? OR ? = '')
          AND (Title LIKE ? OR ? = '')
          AND (Author LIKE ? OR ? = '')
          AND (ISBN LIKE ? OR ? = '')
        """

        # Execute the query
        cursor.execute(query, (category, category, f'%{title}%', title, f'%{author}%', author, f'%{isbn}%', isbn))

        # Fetch all results
        results = cursor.fetchall()

        # Insert results into Treeview
        for row in results:
            cart_tree.insert("", tk.END, values=row)

        connection.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data: {e}")

def remove_cart_item(tree):
    """Remove selected book from the cart."""
    selected_items = tree.selection()
    if selected_items:
        for item in selected_items:
            tree.delete(item)
    else:
        messagebox.showwarning("No Selection", "No book selected for removal.")

def reserve_cart_items(tree, username):
    """Reserve selected books from the cart."""
    selected_items = tree.selection()
    if selected_items:
        try:
            connection = connect_to_db()
            cursor = connection.cursor()
            
            for item in selected_items:
                values = tree.item(item, 'values')
                title, isbn = values

                # Insert into reservation table
                cursor.execute("""
                INSERT INTO tblReserveTransaction (UserID, TransactionNo, DateResreved, ISBN, Notes)
                VALUES (?, NEWID(), GETDATE(), ?, ?)
                """, (username, isbn, "Reserved through GUI"))

            connection.commit()
            connection.close()

            # Remove reserved items from the cart
            remove_cart_item(tree)
            messagebox.showinfo("Success", f"You reserved {len(selected_items)} book(s) in your account.")
        except Exception as e:
            messagebox.showerror("Error", f"Error reserving books: {e}")
    else:
        messagebox.showwarning("No Selection", "No book selected for reservation.")

def setup_return_transaction_interface(tab):
    """Setup the Return Transaction interface."""
    # Add relevant elements and functionalities similar to Borrow Transaction tabs
    pass

def setup_administrative_transactions_interface(tab):
    """Setup the Administrative Transactions interface."""
    # Add relevant elements and functionalities for administrative purposes
    pass

def setup_reservation_interface(tab):
    """Setup the Reservation interface with search functionality."""
    # Header
    header_frame = tk.Frame(tab, bg="#C39898")
    header_frame.pack(fill=tk.X, pady=5)

    tk.Label(header_frame, text="ABC LEARNING RESOURCE CENTER", font=("Arial", 16, "bold"), bg="#C39898").pack(side=tk.LEFT, padx=10)
    tk.Label(header_frame, text="Search Transaction Record", font=("Arial", 14), bg="#C39898").pack(side=tk.RIGHT, padx=10)

    # Search Form
    search_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    search_frame.pack(fill=tk.BOTH, padx=10, pady=10)

    tk.Label(search_frame, text="Transaction No:").pack(anchor="w", padx=10, pady=5)
    transaction_no_entry = tk.Entry(search_frame)
    transaction_no_entry.pack(anchor="w", padx=10, pady=5)

    tk.Label(search_frame, text="ISBN:").pack(anchor="w", padx=10, pady=5)
    isbn_entry = tk.Entry(search_frame)
    isbn_entry.pack(anchor="w", padx=10, pady=5)

    tk.Button(search_frame, text="Search", command=lambda: search_transactions(transaction_no_entry.get(), isbn_entry.get())).pack(pady=10, padx=10)

    # Transaction Records Grid
    transaction_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    transaction_frame.pack(fill=tk.BOTH, padx=10, pady=10)

    tk.Label(transaction_frame, text="Transaction Records", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    global transaction_tree
    transaction_tree = ttk.Treeview(transaction_frame, columns=("transaction_no", "isbn", "date_borrowed"), show="headings")
    transaction_tree.heading("transaction_no", text="Transaction No")
    transaction_tree.heading("isbn", text="ISBN")
    transaction_tree.heading("date_borrowed", text="Date Borrowed")
    transaction_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

def search_books(category, title, author, isbn):
    """Function to search books based on filter criteria and update the UI."""
    # Clear the existing items in the Treeview
    for item in cart_tree.get_children():
        cart_tree.delete(item)

    try:
        # Use the connect_to_db function to establish a database connection
        connection = connect_to_db()
        if connection is None:
            messagebox.showerror("Database Error", "Failed to connect to the database.")
            return  # Exit if connection fails

        cursor = connection.cursor()

        # Construct the SQL query with filter conditions
        query = """
        SELECT Title, ISBN
        FROM tblBooks
        WHERE (Category = ? OR ? = '')
          AND (Title LIKE ? OR ? = '')
          AND (Author LIKE ? OR ? = '')
          AND (ISBN LIKE ? OR ? = '')
        """

        # Execute the query
        cursor.execute(query, (category, category, f'%{title}%', title, f'%{author}%', author, f'%{isbn}%', isbn))
        rows = cursor.fetchall()

        # Populate the Treeview with results
        for row in rows:
            cart_tree.insert("", tk.END, values=row)

    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Database Error", f"An error occurred: {e}")

    finally:
        if connection:
            connection.close()
