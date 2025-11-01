-- Business Management System Database Schema

-- Users Table - Modified to support Owner role and new role structure
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Owner', 'Manager', 'Cashier', 'Accounting')),
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
    is_owner INTEGER DEFAULT 0 CHECK(is_owner IN (0, 1))
);

-- Categories Table - Generic product categories
CREATE TABLE IF NOT EXISTS Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Products Table - Renamed from MenuItems to be more generic
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    price REAL NOT NULL CHECK(price >= 0),
    category_id INTEGER NOT NULL,
    image_path TEXT,
    current_stock INTEGER DEFAULT 0 CHECK(current_stock >= 0),
    is_available INTEGER DEFAULT 1 CHECK(is_available IN (0, 1)),
    FOREIGN KEY (category_id) REFERENCES Categories (category_id) ON DELETE CASCADE
);

-- Sales Locations Table - Renamed from Tables to be more generic
CREATE TABLE IF NOT EXISTS SalesLocations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL UNIQUE,
    capacity INTEGER CHECK(capacity > 0),
    status TEXT DEFAULT 'Available' CHECK(status IN ('Available', 'Occupied', 'Reserved', 'Maintenance'))
);

-- Orders Table - Modified to use generic terminology
CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    user_id_creator INTEGER,
    user_id_processor INTEGER,
    order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Completed', 'Paid', 'Cancelled')),
    total_amount REAL DEFAULT 0.0 CHECK(total_amount >= 0),
    payment_time TIMESTAMP,
    payment_method TEXT,
    FOREIGN KEY (location_id) REFERENCES SalesLocations (location_id),
    FOREIGN KEY (user_id_creator) REFERENCES Users (user_id),
    FOREIGN KEY (user_id_processor) REFERENCES Users (user_id)
);

-- OrderItems Table - Junction table between Orders and Products
CREATE TABLE IF NOT EXISTS OrderItems (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    price_at_order REAL NOT NULL CHECK(price_at_order >= 0),
    subtotal REAL NOT NULL CHECK(subtotal >= 0),
    FOREIGN KEY (order_id) REFERENCES Orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products (product_id) ON DELETE RESTRICT
);

-- InventoryLog Table - Tracks changes to product inventory
CREATE TABLE IF NOT EXISTS InventoryLog (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    change_quantity INTEGER NOT NULL,
    new_stock_level INTEGER NOT NULL CHECK(new_stock_level >= 0),
    reason TEXT NOT NULL CHECK(reason IN ('Sale', 'Manual Stock Entry', 'Spoilage', 'Correction', 'Initial Stock')),
    order_item_id INTEGER,
    user_id_admin INTEGER,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products (product_id) ON DELETE CASCADE,
    FOREIGN KEY (order_item_id) REFERENCES OrderItems (order_item_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id_admin) REFERENCES Users (user_id) ON DELETE SET NULL
);

-- SystemConfig Table - New table for application settings and license information
CREATE TABLE IF NOT EXISTS SystemConfig (
    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id TEXT NOT NULL UNIQUE,
    license_key TEXT NOT NULL,
    business_name TEXT NOT NULL,
    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_validation_date TIMESTAMP,
    is_valid INTEGER DEFAULT 1 CHECK(is_valid IN (0, 1)),
    hardware_id TEXT NOT NULL,
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES Users (user_id)
);

-- AuditLog Table - New table for tracking security-relevant actions
CREATE TABLE IF NOT EXISTS AuditLog (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action_type TEXT NOT NULL,
    action_details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

-- LicenseValidation Table - New table for tracking license validation attempts
CREATE TABLE IF NOT EXISTS LicenseValidation (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_successful INTEGER DEFAULT 0 CHECK(is_successful IN (0, 1)),
    validation_method TEXT NOT NULL,
    error_message TEXT
);
