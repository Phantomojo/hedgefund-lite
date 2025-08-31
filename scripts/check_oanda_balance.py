#!/usr/bin/env python3
"""
Check OANDA Account Balance
"""

import requests
import json

# OANDA API Configuration
OANDA_API_KEY = "1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd"
OANDA_ACCOUNT_ID = "101-001-36248121-001"
OANDA_BASE_URL = "https://api-fxpractice.oanda.com"

def check_account_details():
    """Check OANDA account details and balance."""
    try:
        print("🔍 Checking OANDA Account Details...")
        print("=" * 50)
        
        # Get account details
        url = f"{OANDA_BASE_URL}/v3/accounts/{OANDA_ACCOUNT_ID}"
        headers = {
            "Authorization": f"Bearer {OANDA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            account_data = response.json()
            account = account_data.get('account', {})
            
            print(f"✅ Account Found!")
            print(f"📊 Account ID: {account.get('id')}")
            print(f"💰 Balance: {account.get('balance')} {account.get('currency')}")
            print(f"📈 P&L: {account.get('pl')} {account.get('currency')}")
            print(f"🎯 Unrealized P&L: {account.get('unrealizedPL')} {account.get('currency')}")
            print(f"📊 NAV: {account.get('NAV')} {account.get('currency')}")
            print(f"🔒 Margin Used: {account.get('marginUsed')} {account.get('currency')}")
            print(f"💳 Margin Available: {account.get('marginAvailable')} {account.get('currency')}")
            print(f"📊 Open Trade Count: {account.get('openTradeCount')}")
            print(f"📈 Open Position Count: {account.get('openPositionCount')}")
            print(f"📊 Pending Order Count: {account.get('pendingOrderCount')}")
            print(f"🌍 Currency: {account.get('currency')}")
            print(f"📅 Created Time: {account.get('createdTime')}")
            print(f"🔄 Financing: {account.get('financing')} {account.get('currency')}")
            print(f"📊 Commission: {account.get('commission')} {account.get('currency')}")
            
            return True
            
        else:
            print(f"❌ Failed to get account details: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking account: {str(e)}")
        return False

def check_accounts_list():
    """Check all available accounts."""
    try:
        print("\n🔍 Checking All Available Accounts...")
        print("=" * 50)
        
        url = f"{OANDA_BASE_URL}/v3/accounts"
        headers = {
            "Authorization": f"Bearer {OANDA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            accounts_data = response.json()
            accounts = accounts_data.get('accounts', [])
            
            print(f"📊 Found {len(accounts)} account(s):")
            
            for i, account in enumerate(accounts, 1):
                print(f"\n{i}. Account Details:")
                print(f"   ID: {account.get('id')}")
                print(f"   Name: {account.get('name')}")
                print(f"   Currency: {account.get('currency')}")
                print(f"   Type: {account.get('type')}")
                print(f"   Created: {account.get('createdTime')}")
                
            return True
            
        else:
            print(f"❌ Failed to get accounts list: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking accounts list: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 OANDA Account Balance Checker")
    print("=" * 50)
    
    # Check all accounts first
    check_accounts_list()
    
    # Check specific account details
    print("\n" + "=" * 50)
    check_account_details()
    
    print("\n" + "=" * 50)
    print("✅ Account check complete!")

if __name__ == "__main__":
    main()
