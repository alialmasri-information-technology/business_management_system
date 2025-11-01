#!/usr/bin/env python3
import sqlite3
import bcrypt
import os
import uuid
import platform
import hashlib
import json
import datetime
from typing import Tuple, Optional, Dict, Any, List

# Constants
DATABASE_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "business_management.db")

# Platform-specific imports
try:
    import winreg
    WINDOWS_PLATFORM = True
except ImportError:
    WINDOWS_PLATFORM = False

LICENSE_REGISTRY_KEY = r"SOFTWARE\BusinessManagementSystem"
LICENSE_REGISTRY_VALUE = "LicenseData"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password

def check_password(password: str, hashed_password: bytes) -> bool:
    """Checks if the provided password matches the hashed password."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)

def add_user(username: str, password: str, role: str, full_name: str = "", is_owner: bool = False) -> bool:
    """
    Adds a new user to the Users table.
    
    Args:
        username: User's login name
        password: User's password (will be hashed)
        role: User's role (Owner, Manager, Cashier, Accounting)
        full_name: User's full name
        is_owner: Whether this user is the system owner
        
    Returns:
        True on success, False otherwise
    """
    hashed_pw = hash_password(password)
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if trying to create an Owner when one already exists
        if role == "Owner" or is_owner:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE role = 'Owner' OR is_owner = 1")
            owner_count = cursor.fetchone()[0]
            if owner_count > 0:
                print("Error: An Owner account already exists.")
                return False
        
        cursor.execute("""
            INSERT INTO Users (username, password_hash, role, full_name, is_owner)
            VALUES (?, ?, ?, ?, ?)
        """, (username, hashed_pw, role, full_name, 1 if is_owner else 0))
        conn.commit()
        
        # Log the action
        user_id = cursor.lastrowid
        log_action(None, "USER_CREATED", f"Created user {username} with role {role}")
        
        print(f"User {username} added successfully with role {role}.")
        return True
    except sqlite3.IntegrityError:  # Handles UNIQUE constraint violation for username
        print(f"Error: Username {username} already exists.")
        return False
    except sqlite3.Error as e:
        print(f"Database error while adding user: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verify_user(username: str, password: str) -> Tuple[bool, Optional[str], Optional[int], Optional[bool]]:
    """
    Verifies user credentials.
    
    Args:
        username: User's login name
        password: User's password
        
    Returns:
        Tuple of (success_status, user_role, user_id, is_owner)
    """
    conn = None
    try:
        # First, verify the license is valid
        if not verify_license():
            print("License validation failed. Access denied.")
            return False, None, None, None
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, password_hash, role, is_owner FROM Users WHERE username = ? AND is_active = 1", 
            (username,)
        )
        user_record = cursor.fetchone()

        if user_record:
            if check_password(password, user_record["password_hash"]):
                is_owner = bool(user_record["is_owner"])
                print(f"User {username} verified successfully. Role: {user_record['role']}, Owner: {is_owner}")
                
                # Log the successful login
                log_action(user_record["user_id"], "USER_LOGIN", f"User {username} logged in")
                
                return True, user_record["role"], user_record["user_id"], is_owner
            else:
                print(f"Invalid password for user {username}.")
                
                # Log the failed login attempt
                log_action(None, "LOGIN_FAILED", f"Failed login attempt for user {username}")
                
                return False, None, None, None
        else:
            print(f"User {username} not found or is inactive.")
            return False, None, None, None
    except sqlite3.Error as e:
        print(f"Database error during user verification: {e}")
        return False, None, None, None
    finally:
        if conn:
            conn.close()

def get_hardware_id() -> str:
    """
    Generates a unique hardware identifier based on system components.
    
    Returns:
        A string representing the hardware identifier
    """
    try:
        # Collect hardware information
        system_info = {
            "processor": platform.processor(),
            "machine": platform.machine(),
            "node": platform.node(),
            "system": platform.system(),
            "system_uuid": get_system_uuid()
        }
        
        # Create a stable string representation and hash it
        hardware_str = json.dumps(system_info, sort_keys=True)
        return hashlib.sha256(hardware_str.encode()).hexdigest()
    except Exception as e:
        print(f"Error generating hardware ID: {e}")
        return "unknown_hardware"

def get_system_uuid() -> str:
    """
    Gets the system UUID from Windows WMI or Linux system.
    
    Returns:
        System UUID string
    """
    try:
        if platform.system() == "Windows":
            try:
                import wmi
                c = wmi.WMI()
                for system in c.Win32_ComputerSystemProduct():
                    return system.UUID
            except ImportError:
                # WMI not available
                pass
        elif platform.system() == "Linux":
            # Try to get machine-id on Linux
            if os.path.exists('/etc/machine-id'):
                with open('/etc/machine-id', 'r') as f:
                    return f.read().strip()
        return "unknown"
    except:
        return "unknown"

def generate_license_key(hardware_id: str, owner_info: Dict[str, Any]) -> str:
    """
    Generates a license key based on hardware ID and owner information.
    
    Args:
        hardware_id: Unique hardware identifier
        owner_info: Dictionary containing owner information
        
    Returns:
        Encrypted license key string
    """
    # Create license data
    license_data = {
        "hardware_id": hardware_id,
        "owner_id": owner_info.get("user_id"),
        "owner_name": owner_info.get("full_name"),
        "issue_date": datetime.datetime.now().isoformat(),
        "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=3650)).isoformat(),  # 10 years
        "license_version": "1.0"
    }
    
    # Convert to string and encrypt (simple encryption for demonstration)
    license_str = json.dumps(license_data)
    encrypted = simple_encrypt(license_str)
    
    return encrypted

def simple_encrypt(text: str) -> str:
    """
    Simple encryption function (for demonstration purposes).
    In a real implementation, use proper encryption libraries.
    
    Args:
        text: Text to encrypt
        
    Returns:
        Encrypted string
    """
    # This is a placeholder for actual encryption
    # In a real implementation, use proper encryption like AES
    key = "BusinessManagementSystemSecretKey"
    result = ""
    for i, char in enumerate(text):
        key_char = key[i % len(key)]
        result += chr((ord(char) + ord(key_char)) % 256)
    
    # Convert to hex for storage
    return ''.join(f'{ord(c):02x}' for c in result)

def simple_decrypt(encrypted_hex: str) -> str:
    """
    Simple decryption function (for demonstration purposes).
    
    Args:
        encrypted_hex: Encrypted hex string
        
    Returns:
        Decrypted string
    """
    # Convert from hex
    encrypted = ''.join(chr(int(encrypted_hex[i:i+2], 16)) for i in range(0, len(encrypted_hex), 2))
    
    key = "BusinessManagementSystemSecretKey"
    result = ""
    for i, char in enumerate(encrypted):
        key_char = key[i % len(key)]
        result += chr((ord(char) - ord(key_char)) % 256)
    
    return result

def store_license_in_registry(license_key: str) -> bool:
    """
    Stores the license key in the Windows registry.
    
    Args:
        license_key: License key to store
        
    Returns:
        True if successful, False otherwise
    """
    if not WINDOWS_PLATFORM:
        print("Registry storage only available on Windows")
        return False
        
    try:
        # Create or open the registry key
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, LICENSE_REGISTRY_KEY)
        
        # Set the license value
        winreg.SetValueEx(key, LICENSE_REGISTRY_VALUE, 0, winreg.REG_SZ, license_key)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error storing license in registry: {e}")
        return False

def get_license_from_registry() -> Optional[str]:
    """
    Retrieves the license key from the Windows registry.
    
    Returns:
        License key string or None if not found
    """
    if not WINDOWS_PLATFORM:
        print("Registry access only available on Windows")
        return None
        
    try:
        # Open the registry key
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, LICENSE_REGISTRY_KEY)
        
        # Get the license value
        license_key, _ = winreg.QueryValueEx(key, LICENSE_REGISTRY_VALUE)
        winreg.CloseKey(key)
        return license_key
    except Exception as e:
        print(f"Error retrieving license from registry: {e}")
        return None

def initialize_system(owner_username: str, owner_password: str, owner_full_name: str, business_name: str) -> bool:
    """
    Initializes the system with owner account and license.
    
    Args:
        owner_username: Owner's username
        owner_password: Owner's password
        owner_full_name: Owner's full name
        business_name: Name of the business
        
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if system is already initialized
        cursor.execute("SELECT COUNT(*) FROM SystemConfig")
        if cursor.fetchone()[0] > 0:
            print("System is already initialized.")
            return False
        
        # Create owner account
        if not add_user(owner_username, owner_password, "Owner", owner_full_name, True):
            print("Failed to create owner account.")
            return False
        
        # Get owner ID
        cursor.execute("SELECT user_id FROM Users WHERE username = ?", (owner_username,))
        owner_id = cursor.fetchone()["user_id"]
        
        # Generate hardware ID
        hardware_id = get_hardware_id()
        
        # Generate installation ID
        installation_id = str(uuid.uuid4())
        
        # Generate license key
        owner_info = {"user_id": owner_id, "full_name": owner_full_name}
        license_key = generate_license_key(hardware_id, owner_info)
        
        # Store system configuration
        cursor.execute("""
            INSERT INTO SystemConfig 
            (installation_id, license_key, business_name, hardware_id, owner_id)
            VALUES (?, ?, ?, ?, ?)
        """, (installation_id, license_key, business_name, hardware_id, owner_id))
        
        # Store license in registry (Windows only)
        if WINDOWS_PLATFORM:
            store_license_in_registry(license_key)
        
        # Log the initialization
        log_action(owner_id, "SYSTEM_INITIALIZED", f"System initialized for business: {business_name}")
        
        conn.commit()
        print(f"System initialized successfully for {business_name}.")
        return True
    except sqlite3.Error as e:
        print(f"Database error during system initialization: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def verify_license() -> bool:
    """
    Verifies that the current license is valid.
    
    Returns:
        True if license is valid, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get system configuration
        cursor.execute("SELECT license_key, hardware_id, last_validation_date FROM SystemConfig LIMIT 1")
        config = cursor.fetchone()
        
        if not config:
            log_license_validation(False, "offline", "No system configuration found")
            return False
        
        # Check hardware ID
        current_hardware_id = get_hardware_id()
        if current_hardware_id != config["hardware_id"]:
            log_license_validation(False, "offline", "Hardware ID mismatch")
            return False
        
        # Check if we need to validate online (e.g., once per month)
        need_online_validation = False
        if config["last_validation_date"]:
            last_validation = datetime.datetime.fromisoformat(config["last_validation_date"])
            days_since_validation = (datetime.datetime.now() - last_validation).days
            if days_since_validation > 30:  # Validate online once per month
                need_online_validation = True
        else:
            need_online_validation = True
        
        # Perform online validation if needed
        if need_online_validation:
            # In a real implementation, this would contact a license server
            # For this demo, we'll simulate a successful validation
            online_valid = simulate_online_validation(config["license_key"])
            
            if online_valid:
                # Update last validation date
                cursor.execute(
                    "UPDATE SystemConfig SET last_validation_date = ?", 
                    (datetime.datetime.now().isoformat(),)
                )
                conn.commit()
                log_license_validation(True, "online", "License validated online")
            else:
                log_license_validation(False, "online", "Online validation failed")
                return False
        
        # License is valid
        log_license_validation(True, "offline", "License validated locally")
        return True
    except Exception as e:
        print(f"Error verifying license: {e}")
        log_license_validation(False, "offline", f"Error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def simulate_online_validation(license_key: str) -> bool:
    """
    Simulates online license validation.
    In a real implementation, this would contact a license server.
    
    Args:
        license_key: License key to validate
        
    Returns:
        True if license is valid, False otherwise
    """
    # For demonstration purposes, always return True
    # In a real implementation, this would make an API call to a license server
    return True

def log_license_validation(is_successful: bool, validation_method: str, message: str = "") -> None:
    """
    Logs a license validation attempt.
    
    Args:
        is_successful: Whether validation was successful
        validation_method: Method used for validation (online/offline)
        message: Additional message
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO LicenseValidation 
            (is_successful, validation_method, error_message)
            VALUES (?, ?, ?)
        """, (1 if is_successful else 0, validation_method, message))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging license validation: {e}")
    finally:
        if conn:
            conn.close()

def log_action(user_id: Optional[int], action_type: str, action_details: str) -> None:
    """
    Logs a user action in the audit log.
    
    Args:
        user_id: ID of the user performing the action (can be None)
        action_type: Type of action
        action_details: Details of the action
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO AuditLog 
            (user_id, action_type, action_details)
            VALUES (?, ?, ?)
        """, (user_id, action_type, action_details))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging action: {e}")
    finally:
        if conn:
            conn.close()

def is_system_initialized() -> bool:
    """
    Checks if the system has been initialized.
    
    Returns:
        True if initialized, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM SystemConfig")
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print(f"Error checking system initialization: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Gets user information by ID.
    
    Args:
        user_id: User ID to look up
        
    Returns:
        Dictionary with user information or None if not found
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return dict(user)
        return None
    except sqlite3.Error as e:
        print(f"Error getting user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_users() -> List[Dict[str, Any]]:
    """
    Gets all users in the system.
    
    Returns:
        List of dictionaries with user information
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, role, full_name, is_active, is_owner FROM Users")
        users = cursor.fetchall()
        return [dict(user) for user in users]
    except sqlite3.Error as e:
        print(f"Error getting users: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_user(user_id: int, role: Optional[str] = None, 
                full_name: Optional[str] = None, is_active: Optional[bool] = None,
                password: Optional[str] = None) -> bool:
    """
    Updates user information.
    
    Args:
        user_id: ID of the user to update
        role: New role (optional)
        full_name: New full name (optional)
        is_active: New active status (optional)
        password: New password (optional)
        
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists and is not the owner (if trying to change role)
        cursor.execute("SELECT is_owner FROM Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            print(f"User with ID {user_id} not found.")
            return False
        
        # Don't allow changing owner's role
        if user["is_owner"] and role and role != "Owner":
            print("Cannot change the role of the owner.")
            return False
        
        # Build update query
        query_parts = []
        params = []
        
        if role is not None:
            query_parts.append("role = ?")
            params.append(role)
        
        if full_name is not None:
            query_parts.append("full_name = ?")
            params.append(full_name)
        
        if is_active is not None:
            query_parts.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if password is not None:
            query_parts.append("password_hash = ?")
            params.append(hash_password(password))
        
        if not query_parts:
            print("No updates specified.")
            return False
        
        # Complete the query
        query = f"UPDATE Users SET {', '.join(query_parts)} WHERE user_id = ?"
        params.append(user_id)
        
        # Execute the update
        cursor.execute(query, params)
        conn.commit()
        
        # Log the action
        log_action(None, "USER_UPDATED", f"Updated user with ID {user_id}")
        
        print(f"User with ID {user_id} updated successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Database error updating user: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_business_info() -> Optional[Dict[str, Any]]:
    """
    Gets business information from system configuration.
    
    Returns:
        Dictionary with business information or None if not found
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT business_name, installation_date FROM SystemConfig LIMIT 1")
        info = cursor.fetchone()
        if info:
            return dict(info)
        return None
    except sqlite3.Error as e:
        print(f"Error getting business info: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_business_info(business_name: str) -> bool:
    """
    Updates business information.
    
    Args:
        business_name: New business name
        
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE SystemConfig SET business_name = ?", (business_name,))
        conn.commit()
        
        # Log the action
        log_action(None, "BUSINESS_INFO_UPDATED", f"Updated business name to {business_name}")
        
        print(f"Business information updated successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Database error updating business info: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# Example of how to add default users (run this once manually or via a setup script)
if __name__ == "__main__":
    # This script assumes it's in src/db and business_management.db is at the project root.
    db_path_check = os.path.abspath(DATABASE_NAME)
    print(f"Looking for database at: {db_path_check}")
    
    if not os.path.exists(db_path_check):
        print(f"Database file not found at {db_path_check}. Please run setup_database.py first.")
    else:
        print("Database found. Checking system initialization.")
        
        if not is_system_initialized():
            print("System not initialized. Initializing with default owner...")
            initialize_system("owner", "owner123", "System Owner", "Demo Business")
        else:
            print("System already initialized.")
