import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from login import open_login_window
from database import connect_to_db
from datetime import datetime, timedelta
import logging


class BookManager:
    def __init__(self, root, username="Guest"):
        self.root = root
        self.root.title("ABC Learning Resource Center")
        self.root.geometry("900x600")
        self.current_book_index = -1
        self.rows = []
        self.username = username  # Set username when user logs in

        # Setup UI components
        self.setup_main_window()
        logging.info(f'BookManager initialized with user {self.username}')

    def update_book_info(self, book):
        """Update the book information labels."""
        if not book:
            return
        self.title_value.config(text=book[1])
        self.author_value.config(text=book[2])
        self.isbn_value.config(text=book[0])
        self.stock_value.config(text=str(book[4]))  # Assuming stock is in the 5th column
        self.abstract_text.delete('1.0', tk.END)
        self.abstract_text.insert(tk.END, book[3])  # Assuming abstract is in the 4th column

    def search_books(self):
        """Search books based on input filters."""
        category = self.category_combobox.get()
        title = self.title_entry.get()
        author = self.author_entry.get()
        isbn = self.isbn_entry.get()

        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return

        cursor = conn.cursor()

        # SQL query construction based on inputs
        query = """
        SELECT ISBN, Title, Author, Abstract, InStock
        FROM tblBooks
        WHERE 1=1
        """
        parameters = []
        if category and category != "All":
            query += " AND Category=?"
            parameters.append(category)
        if title:
            query += " AND Title LIKE ?"
            parameters.append(f"%{title}%")
        if author:
            query += " AND Author LIKE ?"
            parameters.append(f"%{author}%")
        if isbn:
            query += " AND ISBN=?"
            parameters.append(isbn)

        try:
            cursor.execute(query, parameters)
            self.rows = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.rows = []

        self.book_listbox.delete(0, tk.END)  # Clear previous search results
        if not self.rows:
            self.book_listbox.insert(tk.END, "No results found.")
            self.update_book_info(("", "", "", "", 0))
        else:
            for row in self.rows:
                self.book_listbox.insert(tk.END, row[1])  # Assuming title is in the 2nd column
            self.display_book(0)

        conn.close()

    def display_book(self, index):
        """Display the selected book's details."""
        if 0 <= index < len(self.rows):
            self.update_book_info(self.rows[index])
            self.current_book_index = index
        else:
            self.update_book_info(("", "", "", "", 0))

    def prev_book(self):
        """Display the previous book in the list."""
        if len(self.rows) > 0 and self.current_book_index > 0:
            self.display_book(self.current_book_index - 1)

    def next_book(self):
        """Display the next book in the list."""
        if len(self.rows) > 0 and self.current_book_index < len(self.rows) - 1:
            self.display_book(self.current_book_index + 1)

    def borrow_book(self):
        """Handle the borrowing of a selected book."""
        if self.current_book_index == -1:
            messagebox.showwarning("No Selection", "Please select a book to borrow.")
            return

        book = self.rows[self.current_book_index]
        isbn = book[0]
        now = datetime.now()
        due_date = now + timedelta(days=14)  # Assume a 2-week borrowing period

        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return

        cursor = conn.cursor()

        try:
            cursor.execute("SELECT InStock FROM tblBooks WHERE ISBN=?", (isbn,))
            stock = cursor.fetchone()[0]

            if stock <= 0:
                messagebox.showwarning("Out of Stock", "This book is currently out of stock.")
                return

            cursor.execute("SELECT UserID FROM tblUser WHERE Username=?", (self.username,))
            user_id = cursor.fetchone()[0]

            cursor.execute("UPDATE tblBooks SET InStock = InStock - 1 WHERE ISBN=?", (isbn,))
            cursor.execute(
                "INSERT INTO tblBorrowTran (UserID, DateBorrowed, ISBN, IsBookReturned, Notes) VALUES (?, ?, ?, ?, ?)",
                (user_id, now.date(), isbn, 0, 'Borrowed')
            )

            conn.commit()
            logging.info(f"User '{self.username}' borrowed book '{book[1]}'. Due date: {due_date.date()}")
            messagebox.showinfo("Success", f"Book '{book[1]}' borrowed successfully. Due date: {due_date.date()}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def setup_main_window(self):
        """Setup the main window and its components."""
        # Header Frame
        header_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, borderwidth=2)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        # Title Label
        title_label = tk.Label(header_frame, text="ABC Learning Resource Center", font=("Arial", 18, "bold"), bg="white")
        title_label.pack(side=tk.LEFT, padx=10)

        # Welcome and Sign In
        welcome_label = tk.Label(header_frame, text=f"Welcome {self.username}!", font=("Arial", 12), bg="white")
        welcome_label.pack(side=tk.RIGHT, padx=10)

        sign_in_button = tk.Button(header_frame, text="Sign In", font=("Arial", 10), command=open_login_window)
        sign_in_button.pack(side=tk.RIGHT, padx=10)

        # Tabs for Search and Reserve / Transaction Record
        tab_control = ttk.Notebook(self.root)
        search_tab = ttk.Frame(tab_control)
        transaction_tab = ttk.Frame(tab_control)

        tab_control.add(search_tab, text="Search and Reserve")
        tab_control.add(transaction_tab, text="Transaction Record")
        tab_control.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

        # Main content frame
        content_frame = tk.Frame(search_tab, relief=tk.RIDGE, borderwidth=2)
        content_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        # Book List Section (Left)
        book_list_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
        book_list_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        book_list_label = tk.Label(book_list_frame, text="Book List", font=("Arial", 12, "bold"), bg="white")
        book_list_label.pack(padx=10, pady=5)

        self.book_listbox = tk.Listbox(book_list_frame, height=20, width=50)
        self.book_listbox.pack(padx=10, pady=10)

        self.book_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        # Book Information Section (Right)
        book_info_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
        book_info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        book_info_label = tk.Label(book_info_frame, text="Book Information", font=("Arial", 12, "bold"), bg="white")
        book_info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w", columnspan=2)

        # Book Details
        title_label = tk.Label(book_info_frame, text="Title", bg="white")
        title_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        author_label = tk.Label(book_info_frame, text="Author", bg="white")
        author_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        isbn_label = tk.Label(book_info_frame, text="ISBN", bg="white")
        isbn_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        stock_label = tk.Label(book_info_frame, text="Stock", bg="white")
        stock_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        # Text Entries for Book Information
        self.title_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.title_value.grid(row=1, column=1, padx=10, pady=5)

        self.author_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.author_value.grid(row=2, column=1, padx=10, pady=5)

        self.isbn_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.isbn_value.grid(row=3, column=1, padx=10, pady=5)

        self.stock_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.stock_value.grid(row=4, column=1, padx=10, pady=5)

        # Book Abstract Text Box
        abstract_label = tk.Label(book_info_frame, text="Abstract", bg="white")
        abstract_label.grid(row=5, column=0, padx=10, pady=5, sticky="ne")

        self.abstract_text = tk.Text(book_info_frame, width=30, height=5, wrap=tk.WORD)
        self.abstract_text.grid(row=5, column=1, padx=10, pady=5)

        # Navigation Buttons
        navigation_frame = tk.Frame(content_frame, bg="white")
        navigation_frame.grid(row=1, column=0, columnspan=2, pady=10)

        prev_button = tk.Button(navigation_frame, text="Previous", command=self.prev_book)
        prev_button.pack(side=tk.LEFT, padx=10)

        next_button = tk.Button(navigation_frame, text="Next", command=self.next_book)
        next_button.pack(side=tk.LEFT, padx=10)

        borrow_button = tk.Button(navigation_frame, text="Borrow", command=self.borrow_book)
        borrow_button.pack(side=tk.LEFT, padx=10)

        # Filter Section
        filter_frame = tk.Frame(search_tab, relief=tk.RIDGE, borderwidth=2)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        category_label = tk.Label(filter_frame, text="Category", font=("Arial", 10))
        category_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.category_combobox = ttk.Combobox(filter_frame, values=["All", "Fiction", "Non-Fiction", "Science", "Technology", "Databases"], state="readonly")
        self.category_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        title_label = tk.Label(filter_frame, text="Title", font=("Arial", 10))
        title_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.title_entry = tk.Entry(filter_frame)
        self.title_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        author_label = tk.Label(filter_frame, text="Author", font=("Arial", 10))
        author_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.author_entry = tk.Entry(filter_frame)
        self.author_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        isbn_label = tk.Label(filter_frame, text="ISBN", font=("Arial", 10))
        isbn_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        self.isbn_entry = tk.Entry(filter_frame)
        self.isbn_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        search_button = tk.Button(filter_frame, text="Search", command=self.search_books)
        search_button.grid(row=4, column=0, columnspan=2, pady=10)

    def on_listbox_select(self, event):
        """Handle the book selection from the listbox."""
        selected_index = self.book_listbox.curselection()
        if selected_index:
            self.display_book(selected_index[0])
        else:
            self.update_book_info(("", "", "", "", 0))

    def load_transactions(self):
        """Load and display user transactions."""
        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return

        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.Title, br.DateBorrowed, br.IsBookReturned, rt.DateReturned, rt.Overdue, rt.Status
            FROM tblBorrowTran br
            LEFT JOIN tblBooks b ON br.ISBN = b.ISBN
            LEFT JOIN tblReturnTran rt ON br.TransactionNo = rt.BTransactionNo
            WHERE br.UserID = (SELECT UserID FROM tblUser WHERE Username = ?)
        """, (self.username,))
        transactions = cursor.fetchall()

        for transaction in transactions:
            logging.info(f"Transaction: {transaction}")

        conn.close()
