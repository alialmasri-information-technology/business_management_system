#!/usr/bin/env python3
import os
import sys
import platform
import shutil
import subprocess
import argparse

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyInstaller
        print("PyInstaller is installed.")
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")
    
    try:
        import customtkinter
        print("CustomTkinter is installed.")
    except ImportError:
        print("CustomTkinter is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
        print("CustomTkinter installed successfully.")
    
    try:
        import bcrypt
        print("Bcrypt is installed.")
    except ImportError:
        print("Bcrypt is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "bcrypt"])
        print("Bcrypt installed successfully.")

def create_spec_file(output_dir, app_name, icon_path=None):
    """Create a PyInstaller spec file."""
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['customtkinter', 'bcrypt'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add all UI files
ui_files = [
    ('src/ui/login_view.py', 'src/ui'),
    ('src/ui/owner_dashboard_view.py', 'src/ui'),
    ('src/ui/manager_dashboard_view.py', 'src/ui'),
    ('src/ui/cashier_dashboard_view.py', 'src/ui'),
    ('src/ui/accounting_dashboard_view.py', 'src/ui'),
    ('src/ui/__init__.py', 'src/ui'),
]
for src, dest in ui_files:
    a.datas += [(dest + '/' + os.path.basename(src), src, 'DATA')]

# Add database files
db_files = [
    ('src/db/database_manager.py', 'src/db'),
    ('src/db/database_schema.sql', 'src/db'),
    ('src/db/__init__.py', 'src/db'),
]
for src, dest in db_files:
    a.datas += [(dest + '/' + os.path.basename(src), src, 'DATA')]

# Add setup script
a.datas += [('setup_database.py', 'setup_database.py', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path if icon_path else ""}',
)
"""
    
    spec_path = os.path.join(output_dir, f"{app_name}.spec")
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    return spec_path

def create_inno_setup_script(output_dir, app_name, version, company_name, exe_path, icon_path=None):
    """Create an Inno Setup script file."""
    iss_content = f"""#define MyAppName "{app_name}"
#define MyAppVersion "{version}"
#define MyAppPublisher "{company_name}"
#define MyAppExeName "{app_name}.exe"

[Setup]
AppId={{{{{app_name}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
OutputDir={output_dir}
OutputBaseFilename={app_name}_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
{'SetupIconFile=' + icon_path if icon_path else ''}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "{exe_path}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{os.path.dirname(exe_path)}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#MyAppName}}}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKLM; Subkey: "SOFTWARE\\{app_name}"; Flags: uninsdeletekey
"""
    
    iss_path = os.path.join(output_dir, f"{app_name}.iss")
    with open(iss_path, 'w') as f:
        f.write(iss_content)
    
    return iss_path

def build_executable(spec_path, output_dir):
    """Build the executable using PyInstaller."""
    print(f"Building executable from {spec_path}...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", spec_path, "--distpath", output_dir])
    print("Executable built successfully.")

def build_installer(iss_path):
    """Build the installer using Inno Setup."""
    if platform.system() != "Windows":
        print("Inno Setup is only available on Windows. Skipping installer creation.")
        return None
    
    print(f"Building installer from {iss_path}...")
    iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not os.path.exists(iscc_path):
        print("Inno Setup not found. Please install Inno Setup 6 and try again.")
        return None
    
    subprocess.check_call([iscc_path, iss_path])
    print("Installer built successfully.")

def obfuscate_python_files(src_dir):
    """Obfuscate Python files to protect source code."""
    try:
        import pyarmor
        print("PyArmor is installed. Obfuscating Python files...")
        
        # Create a list of Python files to obfuscate
        python_files = []
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        # Obfuscate each file
        for file in python_files:
            print(f"Obfuscating {file}...")
            subprocess.check_call([sys.executable, "-m", "pyarmor", "obfuscate", file])
        
        print("Python files obfuscated successfully.")
    except ImportError:
        print("PyArmor is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyarmor"])
        print("PyArmor installed. Please run the script again to obfuscate Python files.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Build Business Management System executable and installer")
    parser.add_argument("--output-dir", default="dist", help="Output directory for the built files")
    parser.add_argument("--app-name", default="BusinessManagementSystem", help="Name of the application")
    parser.add_argument("--version", default="1.0", help="Version of the application")
    parser.add_argument("--company-name", default="Your Company", help="Company name")
    parser.add_argument("--icon-path", help="Path to the application icon")
    parser.add_argument("--obfuscate", action="store_true", help="Obfuscate Python files")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check dependencies
    check_dependencies()
    
    # Obfuscate Python files if requested
    if args.obfuscate:
        obfuscate_python_files("src")
    
    # Create PyInstaller spec file
    spec_path = create_spec_file(args.output_dir, args.app_name, args.icon_path)
    
    # Build executable
    build_executable(spec_path, args.output_dir)
    
    # Create Inno Setup script
    exe_path = os.path.join(args.output_dir, f"{args.app_name}.exe")
    iss_path = create_inno_setup_script(
        args.output_dir, 
        args.app_name, 
        args.version, 
        args.company_name, 
        exe_path, 
        args.icon_path
    )
    
    # Build installer
    if platform.system() == "Windows":
        build_installer(iss_path)
        print(f"Installer created at {args.output_dir}\\{args.app_name}_Setup.exe")
    else:
        print("Installer creation skipped (not on Windows).")
        print(f"Executable created at {exe_path}")

if __name__ == "__main__":
    main()
