@echo off
REM Setup script for the Simple Banking System (Windows)
REM This script installs dependencies, runs tests, and verifies the installation

echo Simple Banking System - Setup Script for Windows
echo ========================================

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo Installing uv package manager...
    pip install uv
    if errorlevel 1 (
        echo Error: Failed to install uv
        pause
        exit /b 1
    )
) else (
    echo uv package manager already installed
)

REM Create virtual environment
echo Creating virtual environment by using uv...
if exist .venv rmdir /s /q .venv
uv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install dependencies
echo Installing dependencies by using uv...
call .venv\Scripts\activate.bat
uv pip install -e .
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

REM Run tests
echo Running test suite...
pytest --cov=banking_system --cov-report=term-missing

echo.
echo Setup completed successfully!
echo.
echo To use the banking system:
echo   1. Activate the virtual environment: .venv\Scripts\activate
echo   2. Run the CLI: python main.py
echo.
echo Data files:
echo   - bank_accounts.csv - Default bank data
echo.

pause 