#!/bin/bash
# Setup script for the Simple Banking System (Unix-based)
# This script installs dependencies, runs tests, and verifies the installation

set -e  # Exit on any error

echo "Simple Banking System - Setup Script for Linux & MacOS (Unix-based)"
echo "========================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.local/bin/env
else
    echo "✅ uv package manager already installed"
fi

# Create virtual environment
echo "Creating virtual environment by using uv..."
uv venv

# Activate virtual environment and install dependencies
echo "Installing dependencies by using uv..."
source .venv/bin/activate
uv pip install -e .

# Run tests
echo "Running test suite..."
pytest --cov=banking_system --cov-report=term-missing

echo ""
echo "Setup completed successfully!"
echo ""
echo "To use the banking system:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run the CLI: python main.py"
echo ""
echo "Data files:"
echo "  - bank_accounts.csv - Default bank data"
echo ""