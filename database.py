import pyodbc
import tkinter as tk
from tkinter import messagebox

# Server and database settings
server = r'LAPTOP-L95224RL'  # Change this if you're using a named instance, e.g., 'LAPTOP-L95224RL\InstanceName'
database = 'Python'

def connect_to_db():
    """Establish a connection to the database using Windows Authentication.""" 
    conn_str = (
        r'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        'Trusted_Connection=yes;'
    )
    try:
        print(f"Connecting to database with connection string: {conn_str}")  # Debugging info
        conn = pyodbc.connect(conn_str)
        print("Connection successful.")
        return conn
    except pyodbc.OperationalError as e:
        display_error("Operational Error", f"OperationalError: {e}")
    except pyodbc.DatabaseError as e:
        display_error("Database Error", f"DatabaseError: {e}")
    except pyodbc.InterfaceError as e:
        display_error("Interface Error", f"InterfaceError: {e}")
    except pyodbc.Error as e:
        display_error("Database Connection Error", f"Error: {e}")
    return None

    # Fetch Users
def fetch_users():
    """Fetch all users from the database."""
    conn = connect_to_db()
    try:
        cursor = conn.cursor()
        query = 'SELECT * FROM tblUsers;'  # Adjust schema if needed
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except pyodbc.Error as e:
        raise RuntimeError(f"Query Error: {e}")
    finally:
        conn.close()

    # Display Error    
def display_error(title, message):
    """Display an error message using Tkinter if initialized.""" 
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(title, message)
    except tk.TclError:
        print(f"{title}: {message}")

# Example usage:
conn = connect_to_db()
if conn:
    # Do something with the connection
    conn.close()
