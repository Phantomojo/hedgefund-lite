# 🤝 Contributing to HedgeFund Lite

Thank you for your interest in contributing to our algorithmic trading system! 🚀

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Security](#security)
- [Community Guidelines](#community-guidelines)

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose
- Git

### Quick Start

1. **Fork the repository**
   ```bash
   git clone https://github.com/Phantomojo/hedgefund-lite.git
   cd hedgefund-lite
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start services**
   ```bash
   docker-compose up -d postgres redis
   ```

5. **Run tests**
   ```bash
   pytest tests/ -v
   ```

## 🛠️ Development Setup

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://trading:trading123@localhost:5432/hedgefund
REDIS_URL=redis://localhost:6379/0

# API Keys (for testing)
OANDA_API_KEY=your_oanda_key
OANDA_ACCOUNT_ID=your_account_id
NEWS_API_KEY=your_news_api_key
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
```

### Database Setup

```bash
# Create database and user
sudo -u postgres psql -c "CREATE ROLE trading WITH PASSWORD 'trading123';"
sudo -u postgres psql -c "CREATE DATABASE hedgefund OWNER trading;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hedgefund TO trading;"

# Run migrations
alembic upgrade head
```

### Running the Application

```bash
# Development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🎨 Code Style

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Import sorting**: Use `isort`
- **Type hints**: Required for all functions
- **Docstrings**: Google style docstrings

### Code Formatting

```bash
# Format code
black src/ tests/ scripts/
isort src/ tests/ scripts/

# Check formatting
black --check --diff src/ tests/ scripts/
isort --check-only --diff src/ tests/ scripts/
```

### Linting

```bash
# Run linters
flake8 src/ tests/ scripts/ --max-line-length=88 --extend-ignore=E203,W503
bandit -r src/
mypy src/
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
├── fixtures/      # Test fixtures
└── conftest.py    # Pytest configuration
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_api.py -v

# Specific test function
pytest tests/unit/test_api.py::test_health_check -v
```

### Test Guidelines

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **E2E tests**: Test complete workflows
- **Mock external services**: Don't make real API calls in tests
- **Test coverage**: Aim for >80% coverage

### Writing Tests

```python
import pytest
from src.api.v1.endpoints import health

def test_health_check():
    """Test health check endpoint."""
    response = health.health_check()
    assert response["status"] == "healthy"
    assert "timestamp" in response

@pytest.mark.asyncio
async def test_async_function():
    """Test async functions."""
    result = await some_async_function()
    assert result is not None
```

## 🔄 Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation if needed
- Follow the code style guidelines

### 3. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new trading strategy

- Implement EMA crossover strategy
- Add unit tests for strategy logic
- Update API documentation
- Fixes #123"
```

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request using the provided template.

### 5. Code Review

- Address review comments
- Ensure all tests pass
- Update documentation if needed
- Get approval from maintainers

### 6. Merge

Once approved, your PR will be merged into the main branch.

## 🐛 Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** for solutions
3. **Try the latest version** of the code

### Creating an Issue

Use the appropriate issue template:
- 🐛 [Bug Report](.github/ISSUE_TEMPLATE/bug_report.yml)
- 🚀 [Feature Request](.github/ISSUE_TEMPLATE/feature_request.yml)
- 🛡️ [Security Vulnerability](.github/ISSUE_TEMPLATE/security_vulnerability.yml)

### Issue Guidelines

- **Be specific**: Provide clear, detailed descriptions
- **Include steps**: Reproduce the issue step by step
- **Add context**: Environment, versions, logs
- **Be respectful**: Maintain a professional tone

## 🔒 Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email: security@hedgefund-lite.com
2. Use the [Security Vulnerability template](.github/ISSUE_TEMPLATE/security_vulnerability.yml)
3. Follow responsible disclosure guidelines

### Security Guidelines

- **No hardcoded secrets** in code
- **Validate all inputs** from users
- **Use parameterized queries** for database operations
- **Implement proper authentication** and authorization
- **Follow OWASP guidelines**

## 👥 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors.

### Communication

- **Be respectful** and professional
- **Use inclusive language**
- **Provide constructive feedback**
- **Help others learn and grow**

### Recognition

Contributors will be recognized in:
- [Contributors list](CONTRIBUTORS.md)
- Release notes
- Project documentation

## 📚 Additional Resources

### Documentation

- [Architecture Guide](ARCHITECTURE_LITE.md)
- [API Documentation](http://localhost:8000/docs)
- [Setup Guide](SETUP_GUIDE.md)
- [Production Guide](PRODUCTION_SUMMARY.md)

### Tools

- **Code Quality**: Black, isort, flake8, bandit, mypy
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Documentation**: MkDocs, Sphinx
- **CI/CD**: GitHub Actions

### Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the docs first
- **Community**: Join our community channels

## 🎯 Contribution Areas

We welcome contributions in these areas:

### 🚀 High Priority
- **Bug fixes** and stability improvements
- **Security enhancements**
- **Performance optimizations**
- **Test coverage improvements**

### 📈 Medium Priority
- **New trading strategies**
- **Additional data sources**
- **UI/UX improvements**
- **Documentation updates**

### 💡 Low Priority
- **Nice-to-have features**
- **Code refactoring**
- **Style improvements**
- **Minor optimizations**

## 🏆 Recognition

### Contributors

We recognize contributors in several ways:

- **Contributors list** in the repository
- **Release notes** for significant contributions
- **Hall of Fame** for major contributors
- **Special thanks** in documentation

### Contribution Levels

- **Bronze**: 1-5 contributions
- **Silver**: 6-20 contributions
- **Gold**: 21-50 contributions
- **Platinum**: 50+ contributions

---

## 📞 Contact

- **General Questions**: Create a GitHub issue
- **Security Issues**: security@hedgefund-lite.com
- **Maintainers**: @Phantomojo

Thank you for contributing to HedgeFund Lite! 🚀

**Last Updated**: 2025-08-31
**Version**: 1.0.0
