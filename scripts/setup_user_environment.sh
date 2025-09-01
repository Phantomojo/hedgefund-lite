#!/bin/bash

# 🔒 USER ENVIRONMENT SETUP SCRIPT
# This script helps users safely configure their trading system

set -e

echo "🚀 HEDGEFUND TRADING SYSTEM - USER SETUP"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root!"
   print_warning "Please run as a regular user with sudo privileges"
   exit 1
fi

print_status "Starting secure environment setup..."

# Step 1: Create user configuration directory
print_status "Creating user configuration directory..."
mkdir -p ~/.hedgefund
print_success "Created ~/.hedgefund directory"

# Step 2: Copy and configure API keys
print_status "Setting up API keys configuration..."
if [ ! -f ~/.hedgefund/api_keys.py ]; then
    cp config/api_keys_example.py ~/.hedgefund/api_keys.py
    print_success "Copied API keys template to ~/.hedgefund/api_keys.py"
    print_warning "Please edit ~/.hedgefund/api_keys.py with your actual API keys"
else
    print_warning "API keys file already exists at ~/.hedgefund/api_keys.py"
fi

# Step 3: Create environment file
print_status "Creating environment configuration..."
cat > ~/.hedgefund/.env << 'EOF'
# HEDGEFUND TRADING SYSTEM - USER ENVIRONMENT
# This file contains your personal configuration
# NEVER commit this file to git!

# Database Configuration
DATABASE_URL=postgresql://trading:your_password@localhost:5432/trading_db
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Notification Webhooks (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Trading Configuration
TRADING_ENABLED=true
MAX_POSITIONS=50
MAX_POSITION_SIZE_PCT=0.02
EMERGENCY_STOP_ENABLED=true

# Risk Management
MAX_PORTFOLIO_LOSS_PCT=0.15
MAX_SINGLE_POSITION_LOSS_PCT=0.25
EOF

print_success "Created environment file at ~/.hedgefund/.env"
print_warning "Please edit ~/.hedgefund/.env with your actual values"

# Step 4: Create user-specific gitignore
print_status "Setting up git protection..."
cat > ~/.hedgefund/.gitignore << 'EOF'
# User-specific gitignore for HedgeFund
# This prevents accidental commits of personal data

# API Keys and Secrets
api_keys.py
.env
*.key
*.pem
*.p12

# Database files
*.db
*.sqlite
*.sqlite3

# Log files
*.log
logs/

# Cache and temporary files
cache/
.cache/
tmp/
temp/
*.tmp

# Personal data
personal_notes.txt
my_strategies/
trading_journal/
EOF

print_success "Created user gitignore at ~/.hedgefund/.gitignore"

# Step 5: Create setup verification script
print_status "Creating setup verification script..."
cat > ~/.hedgefund/verify_setup.py << 'EOF'
#!/usr/bin/env python3
"""
HedgeFund Trading System - Setup Verification
Run this script to verify your configuration is correct
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (MISSING)")
        return False

def check_api_keys():
    """Check if API keys are configured"""
    api_keys_file = Path.home() / ".hedgefund" / "api_keys.py"
    
    if not api_keys_file.exists():
        print("❌ API keys file not found")
        return False
    
    # Read the file and check for template values
    with open(api_keys_file, 'r') as f:
        content = f.read()
    
    template_values = [
        "your_alpha_vantage_api_key_here",
        "your_polygon_api_key_here",
        "your_fred_api_key_here",
        "your_news_api_key_here"
    ]
    
    found_template = False
    for template in template_values:
        if template in content:
            found_template = True
            print(f"⚠️  Found template value: {template}")
    
    if found_template:
        print("❌ Please replace template values with your actual API keys")
        return False
    
    print("✅ API keys appear to be configured")
    return True

def main():
    """Main verification function"""
    print("🔍 HEDGEFUND TRADING SYSTEM - SETUP VERIFICATION")
    print("=" * 50)
    
    # Check required files
    hedgefund_dir = Path.home() / ".hedgefund"
    files_to_check = [
        (hedgefund_dir / "api_keys.py", "API Keys Configuration"),
        (hedgefund_dir / ".env", "Environment Configuration"),
        (hedgefund_dir / ".gitignore", "Git Protection")
    ]
    
    all_files_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    print("\n" + "=" * 50)
    
    # Check API keys
    api_keys_ok = check_api_keys()
    
    print("\n" + "=" * 50)
    
    if all_files_exist and api_keys_ok:
        print("🎉 SETUP VERIFICATION COMPLETE!")
        print("✅ Your HedgeFund trading system is properly configured")
        print("🚀 You can now run the trading system safely")
    else:
        print("⚠️  SETUP VERIFICATION FAILED!")
        print("❌ Please complete the missing configuration steps")
        print("📖 Refer to SECURITY_SETUP.md for detailed instructions")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x ~/.hedgefund/verify_setup.py
print_success "Created setup verification script at ~/.hedgefund/verify_setup.py"

# Step 6: Create user README
print_status "Creating user documentation..."
cat > ~/.hedgefund/README.md << 'EOF'
# 🏠 Personal HedgeFund Configuration

This directory contains your personal HedgeFund trading system configuration.

## 📁 Files in this directory:

- **`api_keys.py`** - Your API keys (NEVER commit this!)
- **`.env`** - Environment variables (NEVER commit this!)
- **`.gitignore`** - Prevents accidental commits of personal data
- **`verify_setup.py`** - Script to verify your configuration

## 🔒 Security Features:

1. **Separate from repository** - Your personal data is never in the main repo
2. **Git protection** - Local .gitignore prevents accidental commits
3. **Template-based** - Uses example files as starting points
4. **User-specific** - Each user has their own configuration

## 🚀 Next Steps:

1. Edit `api_keys.py` with your actual API keys
2. Edit `.env` with your database and other settings
3. Run `python verify_setup.py` to verify configuration
4. Start the trading system!

## ⚠️ Important:

- NEVER commit files from this directory to git
- Keep your API keys secure and private
- Regularly rotate your API keys
- Monitor for any suspicious activity

## 🆘 Need Help?

- Check the main repository's SECURITY_SETUP.md
- Review error messages in the terminal
- Ensure all required services are running
- Verify API key permissions and quotas
EOF

print_success "Created user README at ~/.hedgefund/README.md"

# Step 7: Create symlink for easy access
print_status "Creating configuration symlink..."
if [ ! -L config/user_config.py ]; then
    ln -sf ~/.hedgefund/api_keys.py config/user_config.py
    print_success "Created symlink: config/user_config.py -> ~/.hedgefund/api_keys.py"
else
    print_warning "Symlink already exists"
fi

# Final instructions
echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "✅ Your HedgeFund trading system is now securely configured!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Edit your API keys: nano ~/.hedgefund/api_keys.py"
echo "2. Edit environment: nano ~/.hedgefund/.env"
echo "3. Verify setup: python ~/.hedgefund/verify_setup.py"
echo "4. Start trading: python run_comprehensive_trading.sh"
echo ""
echo "🔒 SECURITY FEATURES ACTIVE:"
echo "- Personal data stored in ~/.hedgefund/"
echo "- Git protection prevents accidental commits"
echo "- Template-based configuration"
echo "- User-specific settings"
echo ""
echo "📖 For detailed instructions, see:"
echo "- SECURITY_SETUP.md (main repository)"
echo "- ~/.hedgefund/README.md (your personal setup)"
echo ""
echo "🚀 Happy trading!"
