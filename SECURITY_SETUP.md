# 🔒 SECURITY SETUP GUIDE - HEDGEFUND TRADING SYSTEM

## 🚨 **CRITICAL SECURITY WARNING**
**NEVER commit your actual API keys, passwords, or personal information to this repository!**

This guide shows you how to safely configure the system with your own credentials.

## 🛡️ **REPOSITORY SECURITY FEATURES**

### **Access Control:**
- ✅ **Public READ access** - Anyone can view and learn from the code
- 🔒 **Protected WRITE access** - Only authorized contributors can modify
- 🚫 **No sensitive data** - All API keys and secrets are protected
- 🔐 **Self-service setup** - Users configure their own credentials

### **Git Protection:**
- `.gitignore` prevents accidental commits of sensitive files
- Repository rules block pushes containing secrets
- Branch protection rules (if enabled by owner)

## 📋 **REQUIRED SETUP STEPS**

### **Step 1: Copy Configuration Template**
```bash
# Copy the template file
cp config/api_keys_example.py config/api_keys.py

# Edit with your actual keys
nano config/api_keys.py
```

### **Step 2: Set Your API Keys**
```python
# Example configuration - REPLACE WITH YOUR ACTUAL KEYS
ALPHA_VANTAGE_API_KEY = "your_actual_key_here"
POLYGON_API_KEY = "your_actual_key_here"
FRED_API_KEY = "your_actual_key_here"
NEWS_API_KEY = "your_actual_key_here"
TWITTER_BEARER_TOKEN = "your_actual_token_here"
```

### **Step 3: Database Setup**
```bash
# PostgreSQL
sudo -u postgres createuser trading
sudo -u postgres createdb trading_db
sudo -u postgres psql -c "ALTER USER trading WITH PASSWORD 'your_secure_password';"

# Redis
sudo systemctl start redis
sudo redis-cli CONFIG SET requirepass "your_redis_password"
```

### **Step 4: Environment Variables (Optional)**
```bash
# Create .env file (automatically ignored by git)
cat > .env << EOF
DATABASE_URL=postgresql://trading:your_password@localhost:5432/trading_db
REDIS_URL=redis://:your_redis_password@localhost:6379/0
SECRET_KEY=your_secret_key_here
EOF
```

## 🔑 **API KEY SOURCES**

### **Free Tier APIs (Limited but Functional):**
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
- **FRED API**: https://fred.stlouisfed.org/docs/api/api_key.html
- **NewsAPI**: https://newsapi.org/ (100 requests/day free)
- **CoinGecko**: https://www.coingecko.com/en/api/pricing

### **Paid APIs (Professional Grade):**
- **Polygon.io**: https://polygon.io/ (Starting $29/month)
- **Twitter API**: https://developer.twitter.com/ (Starting $100/month)
- **OANDA**: https://www.oanda.com/ (Free demo account)

## 🚫 **WHAT NEVER TO COMMIT**

### **Never Commit These Files:**
- `config/api_keys.py` (your actual keys)
- `.env` files
- Database dumps
- Log files with sensitive data
- Personal email addresses
- Real trading account numbers
- Private keys or certificates

### **Safe to Commit:**
- `config/api_keys_example.py` (template)
- Code files
- Documentation
- Configuration templates
- Test files

## 🔐 **ADVANCED SECURITY**

### **Environment-Based Configuration:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Use environment variables
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### **Secret Management:**
```python
# For production systems, use proper secret management
import boto3
from azure.keyvault.secrets import SecretClient

# AWS Secrets Manager
secrets = boto3.client('secretsmanager')
api_key = secrets.get_secret_value(SecretId='trading-api-key')['SecretString']
```

## 🧪 **TESTING YOUR SETUP**

### **Run Security Tests:**
```bash
# Test API connections
python test_all_apis.py

# Test database connections
python -c "from src.core.database import init_db; init_db()"

# Verify no secrets in code
grep -r "your_api_key" src/ || echo "✅ No hardcoded keys found"
```

## 🆘 **TROUBLESHOOTING**

### **Common Issues:**
1. **"API key invalid"** - Check your key and ensure it's active
2. **"Database connection failed"** - Verify PostgreSQL/Redis are running
3. **"Rate limit exceeded"** - Upgrade to paid API tier or wait for reset
4. **"Permission denied"** - Check file permissions and database user access

### **Getting Help:**
- Check the main README.md for setup instructions
- Review error logs in the terminal output
- Ensure all required services are running
- Verify API key permissions and quotas

## 🎯 **SECURITY CHECKLIST**

Before running the system, verify:
- [ ] `config/api_keys.py` contains your actual keys (not template values)
- [ ] Database services are running and accessible
- [ ] API keys are valid and have sufficient quota
- [ ] No sensitive data is committed to git
- [ ] `.env` file exists with your credentials (if using environment variables)
- [ ] File permissions are correct for your user

## 🚀 **READY TO TRADE!**

Once you've completed this setup:
1. Your system will be completely secure
2. No one can access your personal data
3. You can safely share your trading strategies
4. The repository remains open for collaboration
5. Your API keys and secrets are protected

**Remember: Security is a continuous process. Regularly rotate your API keys and monitor for any suspicious activity!**
