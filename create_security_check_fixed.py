#!/usr/bin/env python3
"""
Fixed security check script - ignores false positives
"""
import os
import re
import glob

def check_for_sensitive_patterns():
    """Check code for ACTUAL sensitive data patterns"""
    sensitive_patterns = [
        # Actual sensitive patterns (not including .keys() false positives)
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret_key\s*=\s*["\'][^"\']+["\']',
        r'database_password\s*=\s*["\'][^"\']+["\']',
        r'private_key\s*=\s*["\'][^"\']+["\']',
        r'aws_access_key',
        r'aws_secret_key',
        r'bearer_token',
        r'oauth_token',
    ]
    
    print("🔍 Scanning for ACTUAL sensitive data patterns...")
    
    # Check Python files
    python_files = glob.glob('**/*.py', recursive=True)
    
    issues_found = 0
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for i, line in enumerate(content.splitlines(), 1):
                    for pattern in sensitive_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip if it's just a variable declaration without actual value
                            if re.search(r'=\s*["\'][^"\']*["\']', line):
                                print(f"⚠️  Potential issue in {file_path}:{i}")
                                print(f"   {line.strip()}")
                                issues_found += 1
        except Exception as e:
            print(f"❌ Could not read {file_path}: {e}")
    
    if issues_found == 0:
        print("✅ No sensitive data patterns found!")
    else:
        print(f"🔴 Found {issues_found} potential issues to review")

def check_file_extensions():
    """Check for files with sensitive extensions"""
    sensitive_extensions = ['.key', '.pem', '.cert', '.pfx', '.p12']
    
    print("\n📁 Checking for sensitive file extensions...")
    
    found_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if any(file.endswith(ext) for ext in sensitive_extensions):
                found_files.append(os.path.join(root, file))
    
    if found_files:
        print("⚠️  Found files with sensitive extensions:")
        for file in found_files:
            print(f"   - {file}")
    else:
        print("✅ No files with sensitive extensions found!")

def check_gitignore():
    """Check if .gitignore is properly set up"""
    required_patterns = [
        '__pycache__/',
        '*.pyc',
        '*.log',
        '*.key',
        '*.pem',
        'expenses.json',  # User data should not be in repo
        '*.local',
        'config.ini',
        '.env'
    ]
    
    print("\n📋 Checking .gitignore...")
    
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print("⚠️  Missing patterns in .gitignore:")
            for pattern in missing_patterns:
                print(f"   - {pattern}")
        else:
            print("✅ .gitignore is properly configured!")
    else:
        print("❌ No .gitignore file found!")

if __name__ == "__main__":
    print("🔒 FINAL Security Check for Public Release")
    print("=" * 50)
    check_for_sensitive_patterns()
    check_file_extensions()
    check_gitignore()