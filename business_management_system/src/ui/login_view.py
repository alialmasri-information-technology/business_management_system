#!/usr/bin/env python3
import customtkinter as ctk
from tkinter import messagebox
import os
import sys

# Add the parent directory (src) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database_manager import verify_user, log_action

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Create a stylish login form
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="Business Management System",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(40, 10))
        
        subtitle_label = ctk.CTkLabel(
            self, 
            text="Secure Login",
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Login form container
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(pady=20, padx=40)
        
        # Username
        username_label = ctk.CTkLabel(form_frame, text="Username:", font=ctk.CTkFont(size=14))
        username_label.grid(row=0, column=0, sticky="w", padx=10, pady=(20, 5))
        
        self.username_entry = ctk.CTkEntry(form_frame, width=250, height=35, font=ctk.CTkFont(size=14))
        self.username_entry.grid(row=0, column=1, padx=10, pady=(20, 5))
        
        # Password
        password_label = ctk.CTkLabel(form_frame, text="Password:", font=ctk.CTkFont(size=14))
        password_label.grid(row=1, column=0, sticky="w", padx=10, pady=(10, 20))
        
        self.password_entry = ctk.CTkEntry(form_frame, width=250, height=35, show="*", font=ctk.CTkFont(size=14))
        self.password_entry.grid(row=1, column=1, padx=10, pady=(10, 20))
        self.password_entry.bind("<Return>", lambda event: self.verify_login())
        
        # Login button
        login_button = ctk.CTkButton(
            self, 
            text="Login", 
            command=self.verify_login,
            width=200,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold")
        )
        login_button.pack(pady=20)
        
        # Version info
        version_label = ctk.CTkLabel(
            self, 
            text="Version 1.0",
            font=ctk.CTkFont(size=12)
        )
        version_label.pack(pady=(30, 5))
        
        # Copyright
        copyright_label = ctk.CTkLabel(
            self, 
            text="© 2025 Business Management System",
            font=ctk.CTkFont(size=12)
        )
        copyright_label.pack(pady=(0, 20))
        
        # Set focus to username entry
        self.username_entry.focus_set()
        
    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password.")
            return
        
        success, role, user_id, is_owner = verify_user(username, password)
        
        if success:
            self.controller.login_successful(username, role, user_id, is_owner)
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")
            self.password_entry.delete(0, 'end')
            self.password_entry.focus_set()
