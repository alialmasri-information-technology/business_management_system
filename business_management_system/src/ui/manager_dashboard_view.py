#!/usr/bin/env python3
import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import sys

# Add the parent directory (src) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database_manager import log_action

class ManagerDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Create the manager dashboard UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main title
        title_label = ctk.CTkLabel(
            self, 
            text="Manager Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        welcome_label = ctk.CTkLabel(
            self, 
            text=f"Welcome, {self.controller.current_username}!",
            font=ctk.CTkFont(size=16)
        )
        welcome_label.pack(pady=(0, 20))
        
        # Create tabview for different management sections
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs
        self.tabview.add("Inventory Management")
        self.tabview.add("Sales Overview")
        self.tabview.add("Staff Management")
        self.tabview.add("Reports")
        
        # Set default tab
        self.tabview.set("Inventory Management")
        
        # Populate tabs
        self.setup_inventory_tab()
        self.setup_sales_tab()
        self.setup_staff_tab()
        self.setup_reports_tab()
        
        # Logout button at bottom
        logout_button = ctk.CTkButton(
            self, 
            text="Logout", 
            command=self.logout,
            width=100
        )
        logout_button.pack(pady=(0, 20), padx=20, anchor="se")
        
    def setup_inventory_tab(self):
        tab = self.tabview.tab("Inventory Management")
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            tab,
            text="Inventory Management Features Coming Soon",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
        
    def setup_sales_tab(self):
        tab = self.tabview.tab("Sales Overview")
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            tab,
            text="Sales Overview Features Coming Soon",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
        
    def setup_staff_tab(self):
        tab = self.tabview.tab("Staff Management")
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            tab,
            text="Staff Management Features Coming Soon",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
        
    def setup_reports_tab(self):
        tab = self.tabview.tab("Reports")
        
        # Placeholder content
        placeholder = ctk.CTkLabel(
            tab,
            text="Reports Features Coming Soon",
            font=ctk.CTkFont(size=16)
        )
        placeholder.pack(pady=100)
        
    def logout(self):
        # Log the logout
        log_action(self.controller.current_user_id, "USER_LOGOUT", 
                  f"User {self.controller.current_username} logged out")
                  
        # Reset user info
        self.controller.current_user_role = None
        self.controller.current_user_id = None
        self.controller.current_username = None
        self.controller.is_owner = False
        
        # Show login frame
        self.controller.show_login_frame()
