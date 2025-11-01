#!/usr/bin/env python3
import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import platform
import datetime
import uuid

# Add the parent directory (src) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database_manager import (
    verify_user, add_user, get_db_connection, is_system_initialized,
    initialize_system, verify_license, get_hardware_id, log_action
)

# --- Constants ---
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "business_management.db")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Business Management System")
        self.geometry("900x700")  # Increased default size
        self.current_user_role = None
        self.current_user_id = None
        self.current_username = None
        self.is_owner = False

        # Check if system is initialized
        if not is_system_initialized():
            self.show_initialization_frame()
        else:
            # Verify license before proceeding
            if not verify_license():
                messagebox.showerror("License Error", "Invalid or expired license. Please contact the software vendor.")
                self.quit()
                return
                
            # Container for frames
            self.container = ctk.CTkFrame(self)
            self.container.pack(side="top", fill="both", expand=True)
            self.container.grid_rowconfigure(0, weight=1)
            self.container.grid_columnconfigure(0, weight=1)

            self.frames = {}  # Store instances of frames
            self.show_login_frame()

    def show_initialization_frame(self):
        """Shows the first-run initialization frame for owner setup."""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create initialization frame
        init_frame = ctk.CTkFrame(self)
        init_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            init_frame, 
            text="Business Management System - Initial Setup",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(40, 20))
        
        # Business name
        business_label = ctk.CTkLabel(init_frame, text="Business Name:")
        business_label.pack(pady=(20, 5))
        business_entry = ctk.CTkEntry(init_frame, width=300)
        business_entry.pack(pady=(0, 10))
        
        # Owner information
        owner_frame = ctk.CTkFrame(init_frame)
        owner_frame.pack(pady=10, padx=20, fill="x")
        
        owner_title = ctk.CTkLabel(
            owner_frame, 
            text="Owner Account Setup",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        owner_title.pack(pady=10)
        
        # Owner full name
        name_label = ctk.CTkLabel(owner_frame, text="Full Name:")
        name_label.pack(pady=(10, 5))
        name_entry = ctk.CTkEntry(owner_frame, width=300)
        name_entry.pack(pady=(0, 10))
        
        # Owner username
        username_label = ctk.CTkLabel(owner_frame, text="Username:")
        username_label.pack(pady=(10, 5))
        username_entry = ctk.CTkEntry(owner_frame, width=300)
        username_entry.pack(pady=(0, 10))
        
        # Owner password
        password_label = ctk.CTkLabel(owner_frame, text="Password:")
        password_label.pack(pady=(10, 5))
        password_entry = ctk.CTkEntry(owner_frame, width=300, show="*")
        password_entry.pack(pady=(0, 10))
        
        # Confirm password
        confirm_label = ctk.CTkLabel(owner_frame, text="Confirm Password:")
        confirm_label.pack(pady=(10, 5))
        confirm_entry = ctk.CTkEntry(owner_frame, width=300, show="*")
        confirm_entry.pack(pady=(0, 20))
        
        # Hardware ID display (for information)
        hardware_id = get_hardware_id()
        hardware_label = ctk.CTkLabel(
            init_frame, 
            text=f"Hardware ID: {hardware_id[:8]}...{hardware_id[-8:]}",
            font=ctk.CTkFont(size=12)
        )
        hardware_label.pack(pady=(20, 5))
        
        # Initialize button
        def initialize():
            business_name = business_entry.get().strip()
            owner_name = name_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            # Validate inputs
            if not business_name:
                messagebox.showerror("Validation Error", "Business name is required.")
                return
                
            if not owner_name:
                messagebox.showerror("Validation Error", "Owner name is required.")
                return
                
            if not username:
                messagebox.showerror("Validation Error", "Username is required.")
                return
                
            if not password:
                messagebox.showerror("Validation Error", "Password is required.")
                return
                
            if password != confirm:
                messagebox.showerror("Validation Error", "Passwords do not match.")
                return
            
            # Initialize the system
            if initialize_system(username, password, owner_name, business_name):
                messagebox.showinfo("Setup Complete", 
                                   f"Business Management System has been initialized for {business_name}.\n\n"
                                   f"You can now log in as {username} with the password you provided.")
                
                # Restart the application
                self.destroy()
                app = App()
                app.mainloop()
            else:
                messagebox.showerror("Setup Error", "Failed to initialize the system. Please try again.")
        
        init_button = ctk.CTkButton(
            init_frame, 
            text="Initialize System", 
            command=initialize,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16)
        )
        init_button.pack(pady=30)
        
        # Copyright and version
        version_label = ctk.CTkLabel(
            init_frame, 
            text=f"Business Management System v1.0 | © {datetime.datetime.now().year}",
            font=ctk.CTkFont(size=12)
        )
        version_label.pack(pady=(20, 10))

    def show_frame(self, page_name, *args):
        """Shows a frame for the given page name. Args are passed to the frame constructor."""
        for widget in self.container.winfo_children():
            widget.destroy()

        frame_class = None
        if page_name == "LoginFrame":
            from ui.login_view import LoginFrame
            frame_class = LoginFrame
        elif page_name == "ManagerDashboard":
            from ui.manager_dashboard_view import ManagerDashboard
            frame_class = ManagerDashboard
        elif page_name == "CashierDashboard":
            from ui.cashier_dashboard_view import CashierDashboard
            frame_class = CashierDashboard
        elif page_name == "AccountingDashboard":
            from ui.accounting_dashboard_view import AccountingDashboard
            frame_class = AccountingDashboard
        elif page_name == "OwnerDashboard":
            from ui.owner_dashboard_view import OwnerDashboard
            frame_class = OwnerDashboard
        else:
            # If the requested frame doesn't exist yet, create a placeholder
            frame_class = self.create_placeholder_dashboard(page_name)

        if frame_class:
            frame = frame_class(self.container, self, *args) 
            self.frames[page_name] = frame 
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def create_placeholder_dashboard(self, role_name):
        """Creates a generic placeholder dashboard frame."""
        class PlaceholderDashboard(ctk.CTkFrame):
            def __init__(self, parent, controller, *args):
                super().__init__(parent)
                self.controller = controller
                label = ctk.CTkLabel(
                    self, 
                    text=f"{role_name} Dashboard - Welcome {controller.current_username}!", 
                    font=ctk.CTkFont(size=20, weight="bold")
                )
                label.pack(pady=20, padx=20)

                logout_button = ctk.CTkButton(self, text="Logout", command=self.logout)
                logout_button.pack(pady=10)

            def logout(self):
                self.controller.current_user_role = None
                self.controller.current_user_id = None
                self.controller.current_username = None
                self.controller.is_owner = False
                self.controller.show_login_frame()
                
                # Log the logout
                log_action(self.controller.current_user_id, "USER_LOGOUT", f"User {self.controller.current_username} logged out")
                
        return PlaceholderDashboard

    def show_login_frame(self):
        self.show_frame("LoginFrame")

    def login_successful(self, username, user_role, user_id, is_owner):
        self.current_username = username
        self.current_user_role = user_role
        self.current_user_id = user_id
        self.is_owner = is_owner
        
        messagebox.showinfo("Login Success", f"Welcome {username}! Role: {user_role}")
        
        if is_owner:
            self.show_frame("OwnerDashboard")
        elif user_role == "Manager":
            self.show_frame("ManagerDashboard")
        elif user_role == "Cashier":
            self.show_frame("CashierDashboard")
        elif user_role == "Accounting":
            self.show_frame("AccountingDashboard")
        else:
            messagebox.showerror("Login Error", "Unknown user role.")
            self.show_login_frame()
    
    # Method to get a reference to a currently displayed frame, useful for callbacks
    def get_current_frame_instance(self, frame_name):
        return self.frames.get(frame_name)

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Running setup_database.py first.")
        # Run the database setup script
        setup_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "setup_database.py")
        if os.path.exists(setup_script):
            os.system(f"python {setup_script}")
        else:
            print(f"Setup script not found at {setup_script}.")
            sys.exit(1)
    
    app = App()
    app.mainloop()
