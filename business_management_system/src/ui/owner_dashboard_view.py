#!/usr/bin/env python3
import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import sys

# Add the parent directory (src) to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database_manager import get_all_users, update_user, add_user, get_business_info, update_business_info, log_action

class OwnerDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Create the owner dashboard UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main title
        title_label = ctk.CTkLabel(
            self, 
            text="Owner Dashboard",
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
        self.tabview.add("User Management")
        self.tabview.add("Business Settings")
        self.tabview.add("License Information")
        self.tabview.add("System Logs")
        
        # Set default tab
        self.tabview.set("User Management")
        
        # Populate tabs
        self.setup_user_management_tab()
        self.setup_business_settings_tab()
        self.setup_license_info_tab()
        self.setup_system_logs_tab()
        
        # Logout button at bottom
        logout_button = ctk.CTkButton(
            self, 
            text="Logout", 
            command=self.logout,
            width=100
        )
        logout_button.pack(pady=(0, 20), padx=20, anchor="se")
        
    def setup_user_management_tab(self):
        tab = self.tabview.tab("User Management")
        
        # User list frame
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # User list title
        list_title = ctk.CTkLabel(
            list_frame, 
            text="User Accounts",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.pack(pady=(10, 5), padx=10)
        
        # Create scrollable frame for user list
        scrollable_frame = ctk.CTkScrollableFrame(list_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Populate user list
        self.populate_user_list(scrollable_frame)
        
        # User actions frame
        action_frame = ctk.CTkFrame(tab)
        action_frame.pack(side="right", fill="both", padx=(10, 0), pady=10, expand=True)
        
        # Action title
        action_title = ctk.CTkLabel(
            action_frame, 
            text="Add New User",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        action_title.pack(pady=(10, 15), padx=10)
        
        # New user form
        form_frame = ctk.CTkFrame(action_frame)
        form_frame.pack(fill="x", padx=10, pady=5)
        
        # Username
        username_label = ctk.CTkLabel(form_frame, text="Username:")
        username_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.new_username = ctk.CTkEntry(form_frame, width=200)
        self.new_username.grid(row=0, column=1, padx=10, pady=5)
        
        # Password
        password_label = ctk.CTkLabel(form_frame, text="Password:")
        password_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.new_password = ctk.CTkEntry(form_frame, width=200, show="*")
        self.new_password.grid(row=1, column=1, padx=10, pady=5)
        
        # Full Name
        fullname_label = ctk.CTkLabel(form_frame, text="Full Name:")
        fullname_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.new_fullname = ctk.CTkEntry(form_frame, width=200)
        self.new_fullname.grid(row=2, column=1, padx=10, pady=5)
        
        # Role
        role_label = ctk.CTkLabel(form_frame, text="Role:")
        role_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.new_role = ctk.CTkComboBox(
            form_frame, 
            values=["Manager", "Cashier", "Accounting"],
            width=200
        )
        self.new_role.grid(row=3, column=1, padx=10, pady=5)
        
        # Add user button
        add_button = ctk.CTkButton(
            action_frame, 
            text="Add User", 
            command=self.add_new_user,
            width=150
        )
        add_button.pack(pady=15)
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            action_frame, 
            text="Refresh User List", 
            command=lambda: self.populate_user_list(scrollable_frame),
            width=150
        )
        refresh_button.pack(pady=(5, 15))
        
    def populate_user_list(self, parent_frame):
        # Clear existing widgets
        for widget in parent_frame.winfo_children():
            widget.destroy()
            
        # Get all users
        users = get_all_users()
        
        # Create header
        header_frame = ctk.CTkFrame(parent_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(header_frame, text="Username", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Role", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Status", width=80, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(header_frame, text="Actions", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5)
        
        # Add users to list
        for i, user in enumerate(users):
            row_frame = ctk.CTkFrame(parent_frame)
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row_frame, text=user["username"], width=100).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkLabel(row_frame, text=user["role"], width=100).grid(row=0, column=1, padx=5, pady=5)
            
            status_text = "Active" if user["is_active"] else "Inactive"
            status_color = "green" if user["is_active"] else "red"
            status_label = ctk.CTkLabel(row_frame, text=status_text, width=80, text_color=status_color)
            status_label.grid(row=0, column=2, padx=5, pady=5)
            
            # Only allow actions on non-owner accounts
            if not user["is_owner"]:
                action_frame = ctk.CTkFrame(row_frame)
                action_frame.grid(row=0, column=3, padx=5, pady=2)
                
                toggle_text = "Deactivate" if user["is_active"] else "Activate"
                toggle_button = ctk.CTkButton(
                    action_frame, 
                    text=toggle_text, 
                    width=80,
                    command=lambda u=user: self.toggle_user_status(u, parent_frame)
                )
                toggle_button.pack(side="left", padx=2)
                
                reset_button = ctk.CTkButton(
                    action_frame, 
                    text="Reset PW", 
                    width=80,
                    command=lambda u=user: self.reset_user_password(u)
                )
                reset_button.pack(side="left", padx=2)
            else:
                ctk.CTkLabel(row_frame, text="Owner Account", width=100).grid(row=0, column=3, padx=5, pady=5)
    
    def toggle_user_status(self, user, parent_frame):
        # Toggle user active status
        new_status = not user["is_active"]
        if update_user(user["user_id"], is_active=new_status):
            status_text = "activated" if new_status else "deactivated"
            messagebox.showinfo("User Updated", f"User {user['username']} has been {status_text}.")
            
            # Log the action
            log_action(self.controller.current_user_id, "USER_STATUS_CHANGED", 
                      f"User {user['username']} {status_text} by {self.controller.current_username}")
            
            # Refresh the user list
            self.populate_user_list(parent_frame)
        else:
            messagebox.showerror("Error", f"Failed to update user {user['username']}.")
    
    def reset_user_password(self, user):
        # Ask for new password
        new_password = ctk.CTkInputDialog(
            text=f"Enter new password for {user['username']}:", 
            title="Reset Password"
        ).get_input()
        
        if not new_password:
            return
            
        # Update user password
        if update_user(user["user_id"], password=new_password):
            messagebox.showinfo("Password Reset", f"Password for {user['username']} has been reset.")
            
            # Log the action
            log_action(self.controller.current_user_id, "PASSWORD_RESET", 
                      f"Password reset for user {user['username']} by {self.controller.current_username}")
        else:
            messagebox.showerror("Error", f"Failed to reset password for {user['username']}.")
    
    def add_new_user(self):
        # Get form values
        username = self.new_username.get().strip()
        password = self.new_password.get()
        full_name = self.new_fullname.get().strip()
        role = self.new_role.get()
        
        # Validate inputs
        if not username or not password or not full_name:
            messagebox.showerror("Validation Error", "All fields are required.")
            return
            
        # Add user
        if add_user(username, password, role, full_name):
            messagebox.showinfo("User Added", f"User {username} has been added with role {role}.")
            
            # Log the action
            log_action(self.controller.current_user_id, "USER_ADDED", 
                      f"New user {username} with role {role} added by {self.controller.current_username}")
            
            # Clear form
            self.new_username.delete(0, 'end')
            self.new_password.delete(0, 'end')
            self.new_fullname.delete(0, 'end')
            
            # Refresh user list
            scrollable_frame = self.tabview.tab("User Management").winfo_children()[0].winfo_children()[2]
            self.populate_user_list(scrollable_frame)
        else:
            messagebox.showerror("Error", f"Failed to add user {username}.")
    
    def setup_business_settings_tab(self):
        tab = self.tabview.tab("Business Settings")
        
        # Get current business info
        business_info = get_business_info()
        
        # Settings frame
        settings_frame = ctk.CTkFrame(tab)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Business name
        name_label = ctk.CTkLabel(
            settings_frame, 
            text="Business Name:",
            font=ctk.CTkFont(size=14)
        )
        name_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        self.business_name = ctk.CTkEntry(settings_frame, width=300)
        self.business_name.grid(row=0, column=1, padx=20, pady=(20, 10))
        
        if business_info:
            self.business_name.insert(0, business_info["business_name"])
        
        # Installation date (read-only)
        date_label = ctk.CTkLabel(
            settings_frame, 
            text="Installation Date:",
            font=ctk.CTkFont(size=14)
        )
        date_label.grid(row=1, column=0, sticky="w", padx=20, pady=10)
        
        date_value = "Unknown"
        if business_info and business_info["installation_date"]:
            date_value = business_info["installation_date"]
            
        date_value_label = ctk.CTkLabel(
            settings_frame, 
            text=date_value,
            font=ctk.CTkFont(size=14)
        )
        date_value_label.grid(row=1, column=1, sticky="w", padx=20, pady=10)
        
        # Save button
        save_button = ctk.CTkButton(
            settings_frame, 
            text="Save Changes", 
            command=self.save_business_settings,
            width=150
        )
        save_button.grid(row=2, column=1, sticky="e", padx=20, pady=(20, 10))
        
    def save_business_settings(self):
        # Get form values
        business_name = self.business_name.get().strip()
        
        # Validate inputs
        if not business_name:
            messagebox.showerror("Validation Error", "Business name is required.")
            return
            
        # Update business info
        if update_business_info(business_name):
            messagebox.showinfo("Settings Saved", "Business settings have been updated.")
            
            # Log the action
            log_action(self.controller.current_user_id, "BUSINESS_INFO_UPDATED", 
                      f"Business name updated to {business_name} by {self.controller.current_username}")
        else:
            messagebox.showerror("Error", "Failed to update business settings.")
    
    def setup_license_info_tab(self):
        tab = self.tabview.tab("License Information")
        
        # License info frame
        license_frame = ctk.CTkFrame(tab)
        license_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # License info title
        license_title = ctk.CTkLabel(
            license_frame, 
            text="License Information",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        license_title.pack(pady=(20, 30))
        
        # License details
        info_frame = ctk.CTkFrame(license_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # Product name
        ctk.CTkLabel(info_frame, text="Product:", width=150, anchor="w").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(info_frame, text="Business Management System", width=300, anchor="w").grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Version
        ctk.CTkLabel(info_frame, text="Version:", width=150, anchor="w").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(info_frame, text="1.0", width=300, anchor="w").grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # License type
        ctk.CTkLabel(info_frame, text="License Type:", width=150, anchor="w").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(info_frame, text="Full Commercial License", width=300, anchor="w").grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # License status
        ctk.CTkLabel(info_frame, text="License Status:", width=150, anchor="w").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(info_frame, text="Active", width=300, anchor="w", text_color="green").grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Hardware ID
        from db.database_manager import get_hardware_id
        hardware_id = get_hardware_id()
        
        ctk.CTkLabel(info_frame, text="Hardware ID:", width=150, anchor="w").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(info_frame, text=f"{hardware_id[:8]}...{hardware_id[-8:]}", width=300, anchor="w").grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # Contact info
        contact_frame = ctk.CTkFrame(license_frame)
        contact_frame.pack(fill="x", padx=20, pady=(30, 10))
        
        contact_label = ctk.CTkLabel(
            contact_frame, 
            text="For license inquiries, please contact:",
            font=ctk.CTkFont(size=14)
        )
        contact_label.pack(pady=(10, 5))
        
        email_label = ctk.CTkLabel(
            contact_frame, 
            text="support@businessmanagementsystem.com",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        email_label.pack(pady=(0, 10))
    
    def setup_system_logs_tab(self):
        tab = self.tabview.tab("System Logs")
        
        # Logs frame
        logs_frame = ctk.CTkFrame(tab)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logs title
        logs_title = ctk.CTkLabel(
            logs_frame, 
            text="System Activity Logs",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        logs_title.pack(pady=(10, 5))
        
        # Create scrollable frame for logs
        scrollable_frame = ctk.CTkScrollableFrame(logs_frame, height=400)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Get logs from database
        conn = None
        try:
            from db.database_manager import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get the most recent 100 logs
            cursor.execute("""
                SELECT a.log_id, a.action_type, a.action_details, a.timestamp, u.username
                FROM AuditLog a
                LEFT JOIN Users u ON a.user_id = u.user_id
                ORDER BY a.timestamp DESC
                LIMIT 100
            """)
            
            logs = cursor.fetchall()
            
            # Create header
            header_frame = ctk.CTkFrame(scrollable_frame)
            header_frame.pack(fill="x", pady=(0, 5))
            
            ctk.CTkLabel(header_frame, text="Time", width=150, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkLabel(header_frame, text="User", width=100, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkLabel(header_frame, text="Action", width=120, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5)
            ctk.CTkLabel(header_frame, text="Details", width=300, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5)
            
            # Add logs to list
            for i, log in enumerate(logs):
                row_frame = ctk.CTkFrame(scrollable_frame)
                row_frame.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row_frame, text=log["timestamp"], width=150).grid(row=0, column=0, padx=5, pady=5)
                ctk.CTkLabel(row_frame, text=log["username"] or "System", width=100).grid(row=0, column=1, padx=5, pady=5)
                ctk.CTkLabel(row_frame, text=log["action_type"], width=120).grid(row=0, column=2, padx=5, pady=5)
                ctk.CTkLabel(row_frame, text=log["action_details"], width=300).grid(row=0, column=3, padx=5, pady=5)
                
        except Exception as e:
            error_label = ctk.CTkLabel(
                scrollable_frame, 
                text=f"Error loading logs: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)
        finally:
            if conn:
                conn.close()
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            logs_frame, 
            text="Refresh Logs", 
            command=lambda: self.setup_system_logs_tab(),
            width=150
        )
        refresh_button.pack(pady=10)
        
        # Export logs button
        export_button = ctk.CTkButton(
            logs_frame, 
            text="Export Logs", 
            command=self.export_logs,
            width=150
        )
        export_button.pack(pady=(0, 10))
    
    def export_logs(self):
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Logs"
        )
        
        if not file_path:
            return
            
        # Export logs to CSV
        conn = None
        try:
            from db.database_manager import get_db_connection
            import csv
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get all logs
            cursor.execute("""
                SELECT a.log_id, a.action_type, a.action_details, a.timestamp, u.username
                FROM AuditLog a
                LEFT JOIN Users u ON a.user_id = u.user_id
                ORDER BY a.timestamp DESC
            """)
            
            logs = cursor.fetchall()
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Log ID', 'Timestamp', 'User', 'Action Type', 'Details'])
                
                for log in logs:
                    writer.writerow([
                        log["log_id"],
                        log["timestamp"],
                        log["username"] or "System",
                        log["action_type"],
                        log["action_details"]
                    ])
            
            messagebox.showinfo("Export Complete", f"Logs exported to {file_path}")
            
            # Log the action
            log_action(self.controller.current_user_id, "LOGS_EXPORTED", 
                      f"System logs exported by {self.controller.current_username}")
                      
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export logs: {str(e)}")
        finally:
            if conn:
                conn.close()
    
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
