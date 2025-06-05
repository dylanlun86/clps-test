# Simple Banking System

A simple banking system implementation in Python.


## Features

### Core Banking Operations
- **Create Account**: Register new accounts with names and initial balances
- **Deposit Money**: Add funds to any account with validation
- **Withdraw Money**: Remove funds with overdraft protection
- **Transfer Money**: Move funds between accounts atomically with rollback
- **Check Balance**: View current account balance
- **List Accounts**: Display all accounts with details
- **Bank Summary**: View comprehensive banking statistics

## Quick Start

### Prerequisites
- Python 3.10+
- `uv` package manager (will be installed automatically if missing)

### Installation

**Linux/macOS:**
```bash
# Clone or download the project
# Navigate to project directory
chmod +x setup.sh
./setup.sh
```

**Windows (Batch):**
```cmd
# Navigate to project directory in Command Prompt
setup.bat
```

**Windows (PowerShell):**
```powershell
# Navigate to project directory in PowerShell
PowerShell -ExecutionPolicy Bypass -File setup.ps1
```

**Manual Setup:**
```bash
# Install uv package manager
pip install uv

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate.bat  # Windows

# Install dependencies
uv pip install -e .

# Run tests to verify installation
pytest

# Run the application
python main.py
```

### Running the System

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate.bat  # Windows

# Start the banking system
python main.py
```

## Testing & Coverage

The project includes tests with perfect coverage:

### Test Coverage Results
| Module | Statements | Coverage | Status |
|--------|------------|----------|---------|
| `account.py` | 49 | **100%** |  Perfect |
| `bank.py` | 113 | **100%** |  Perfect |
| `exceptions.py` | 26 | **100%** |  Perfect |
| **Core Business Logic** | **188** | **100%** |  **PERFECT** |

### Running Tests

```bash
# Run all tests (79 tests total)
pytest

# Run specific test categories
pytest tests/test_account.py
pytest tests/test_bank.py
pytest tests/test_bank_edge_cases.py
pytest tests/test_exceptions.py

# View coverage report
open htmlcov/index.html  # Linux/MacOS
start htmlcov/index.html  # Windows
```
