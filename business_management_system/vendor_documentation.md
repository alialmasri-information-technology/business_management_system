# Business Management System - Vendor Documentation

## Introduction

This document provides detailed information for you as the software vendor of the Business Management System. It covers installation, configuration, licensing, and management of the system for your clients.

## System Architecture

The Business Management System is built with the following components:

- **Frontend**: Python with CustomTkinter for the graphical user interface
- **Backend**: SQLite database for data storage
- **Security**: bcrypt for password hashing, custom licensing system
- **Packaging**: PyInstaller for executable creation, Inno Setup for Windows installer

## Installation Process

### For You (Vendor)
1. Use the provided installer scripts to build the application package:
   ```
   python installer/build_installer.py --app-name "BusinessManagementSystem" --company-name "Your Company" --obfuscate
   ```
2. The script will create:
   - A standalone executable using PyInstaller
   - A Windows installer using Inno Setup (Windows only)
   - Obfuscated Python code to protect your intellectual property

### For Your Clients
1. Provide the client with the `BusinessManagementSystem_Setup.exe` installer
2. Guide them through the installation process
3. During first run, you should be present to set up the Owner account (which only you will have access to)

## Owner Account Setup

The Owner account is exclusively for you as the software vendor:

1. When setting up a new installation for a client:
   - Run the application after installation
   - Enter the client's business name
   - Create your Owner account with credentials only you know
   - This Owner account will have exclusive management rights

2. Important security notes:
   - Never share the Owner credentials with clients
   - The Owner account cannot be duplicated or recreated after initial setup
   - All management functions are restricted to the Owner role

## License Management

The system includes a robust licensing system to protect your software:

### How Licensing Works
1. During installation, the system:
   - Generates a unique hardware ID based on the client's computer
   - Creates a license key tied to this hardware ID
   - Stores the license in the database and Windows registry
   - Sets up periodic online validation

2. License validation:
   - Hardware validation occurs on every startup
   - Online validation occurs monthly (configurable)
   - Failed validation will restrict access to the system

### Managing Client Licenses
As the vendor, you can:
1. View license information in the Owner Dashboard
2. Update or renew licenses if needed
3. Transfer licenses to new hardware if a client upgrades their system

## Client Management

### Adding Users for Clients
1. Log in with your Owner account
2. Go to the User Management tab
3. Create accounts for your client's staff:
   - Manager accounts for business managers
   - Cashier accounts for sales staff
   - Accounting accounts for financial staff

### Business Configuration
1. Set up the client's business information:
   - Business name
   - Other configuration as needed

### Training Clients
Provide training for each role:
1. Managers: Inventory, sales overview, staff management
2. Cashiers: Sales terminal, order processing
3. Accounting: Financial reports, expense management

## Customization Options

The system can be customized for different business types:

### Product Categories
1. Log in as Owner
2. Access the database configuration
3. Set up categories appropriate for the client's business

### Business-Specific Settings
Modify the database to include:
1. Custom fields for different business types
2. Industry-specific reporting
3. Specialized inventory management

## Troubleshooting

### Common Client Issues

**Issue**: License validation failures
- Solution: Verify hardware hasn't changed significantly
- Use your Owner account to update the license if needed

**Issue**: Database corruption
- Solution: Restore from backup or repair the database
- Instructions for database repair are in the technical appendix

**Issue**: User access problems
- Solution: Verify user accounts and permissions
- Reset passwords if necessary using your Owner account

### Technical Support Process
1. Remote access the client's system using your preferred tool
2. Log in with your Owner account
3. Check system logs for errors
4. Resolve issues using the Owner-only management functions

## Security Considerations

### Protecting Your Software
The system includes several anti-piracy measures:
1. Hardware-locked licensing
2. Code obfuscation
3. Registry-based license storage
4. Online validation
5. Anti-debugging measures

### Updating Security Measures
Periodically update the security measures:
1. Release updates with improved security
2. Monitor for unauthorized copies
3. Update the licensing system as needed

## Technical Appendix

### Database Schema
The system uses the following key tables:
- Users: Stores user accounts and roles
- Products: Stores inventory items
- Orders/OrderItems: Stores sales transactions
- SystemConfig: Stores license and configuration
- AuditLog: Stores system activity logs

### Customization API
For advanced customization, use the following modules:
- database_manager.py: Database access and management
- main.py: Application entry point and UI management

### Building Custom Extensions
To extend the system:
1. Create new UI views in the src/ui directory
2. Add new database tables as needed
3. Update the main.py file to include your extensions
4. Rebuild the installer

---

© 2025 Business Management System. All rights reserved.
