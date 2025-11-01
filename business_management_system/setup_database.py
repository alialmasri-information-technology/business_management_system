#!/usr/bin/env python3
import sqlite3
import os
import sys

# Add the parent directory (src) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "business_management.db")

def create_database():
    """Creates the database with all tables according to the schema."""
    # Check if database already exists
    if os.path.exists(DB_PATH):
        print(f"Database already exists at {DB_PATH}. Skipping creation.")
        return
    
    print(f"Creating new database at {DB_PATH}...")
    
    # Read the schema SQL file
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "db", "database_schema.sql")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Connect to database (will create it if it doesn't exist)
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute the schema SQL
        cursor.executescript(schema_sql)
        
        # Commit the changes
        conn.commit()
        print("Database created successfully with all tables.")
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def add_sample_data():
    """Adds sample data to the database for testing."""
    from db.database_manager import add_user, initialize_system
    
    # Initialize the system with owner account
    if initialize_system("owner", "owner123", "System Owner", "Demo Business"):
        print("System initialized with owner account.")
    
    # Add sample users
    add_user("manager1", "manager123", "Manager", "John Manager")
    add_user("cashier1", "cashier123", "Cashier", "Jane Cashier")
    add_user("accounting1", "accounting123", "Accounting", "Alex Accountant")
    
    # Add sample categories and products
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Add categories
        categories = [
            ("Electronics", "Electronic devices and accessories"),
            ("Groceries", "Food and household items"),
            ("Clothing", "Apparel and fashion items"),
            ("Office Supplies", "Stationery and office equipment")
        ]
        cursor.executemany("INSERT INTO Categories (name, description) VALUES (?, ?)", categories)
        
        # Add products
        products = [
            ("Smartphone", "Latest model smartphone", 699.99, 1, "smartphone.jpg", 50, 1),
            ("Laptop", "High-performance laptop", 1299.99, 1, "laptop.jpg", 25, 1),
            ("Bread", "Fresh baked bread", 3.99, 2, "bread.jpg", 100, 1),
            ("Milk", "1 gallon of milk", 4.49, 2, "milk.jpg", 75, 1),
            ("T-Shirt", "Cotton t-shirt", 19.99, 3, "tshirt.jpg", 200, 1),
            ("Jeans", "Denim jeans", 49.99, 3, "jeans.jpg", 150, 1),
            ("Notebook", "Spiral notebook", 2.99, 4, "notebook.jpg", 300, 1),
            ("Pen Set", "Set of 10 pens", 8.99, 4, "penset.jpg", 250, 1)
        ]
        cursor.executemany("""
            INSERT INTO Products 
            (name, description, price, category_id, image_path, current_stock, is_available) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, products)
        
        # Add sales locations
        locations = [
            ("Checkout 1", 1, "Available"),
            ("Checkout 2", 1, "Available"),
            ("Checkout 3", 1, "Available"),
            ("Online Store", 999, "Available")
        ]
        cursor.executemany("""
            INSERT INTO SalesLocations
            (location_name, capacity, status)
            VALUES (?, ?, ?)
        """, locations)
        
        conn.commit()
        print("Sample data added successfully.")
    except sqlite3.Error as e:
        print(f"Error adding sample data: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Business Management System - Database Setup")
    print("===========================================")
    
    create_database()
    
    # Ask if user wants to add sample data
    response = input("Do you want to add sample data for testing? (y/n): ")
    if response.lower() == 'y':
        add_sample_data()
    
    print("Database setup complete.")
