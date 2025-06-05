# Simple Banking System - Windows Setup (PowerShell)
# This script installs dependencies, runs tests, and verifies the installation

Write-Host "Simple Banking System - Setup Script for Windows (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if uv is installed
try {
    $uvVersion = uv --version 2>$null
    Write-Host "uv package manager already installed" -ForegroundColor Green
} catch {
    Write-Host "Installing uv package manager..." -ForegroundColor Yellow
    try {
        pip install uv
    } catch {
        Write-Host "Error: Failed to install uv" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Create virtual environment
Write-Host "Creating virtual environment by using uv..." -ForegroundColor Blue
if (Test-Path ".venv") {
    Remove-Item -Recurse -Force .venv
}

try {
    uv venv
} catch {
    Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment and install dependencies
Write-Host "Installing dependencies by using uv..." -ForegroundColor Blue
try {
    & ".venv\Scripts\Activate.ps1"
    uv pip install -e .
} catch {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run tests
Write-Host "Running test suite..." -ForegroundColor Blue
pytest --cov=banking_system --cov-report=term-missing

Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To use the banking system:"
Write-Host "  1. Activate the virtual environment: .venv\Scripts\Activate"
Write-Host "  2. Run the CLI: python main.py"
Write-Host ""
Write-Host "Data files:"
Write-Host "  - bank_accounts.csv - Default bank data"
Write-Host ""

Read-Host "Press Enter to continue" 