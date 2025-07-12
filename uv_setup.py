#!/usr/bin/env python3
"""
UV Setup Script - Environment Management for Lite Workflow
"""

import subprocess
import sys
import os

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_uv_environment():
    """Set up uv environment and install dependencies."""
    print("🚀 Setting up UV environment...")
    
    # Check if uv is installed
    success, stdout, stderr = run_command("uv --version")
    if not success:
        print("❌ UV not found. Installing...")
        
        # Install uv
        install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
        success, stdout, stderr = run_command(install_cmd)
        if not success:
            print(f"❌ Failed to install uv: {stderr}")
            return False
    
    print(f"✅ UV version: {stdout.strip()}")
    
    # Create virtual environment
    print("📦 Creating virtual environment...")
    success, stdout, stderr = run_command("uv venv")
    if not success:
        print(f"❌ Failed to create venv: {stderr}")
        return False
    
    print("✅ Virtual environment created")
    
    # Install dependencies
    print("📥 Installing dependencies...")
    success, stdout, stderr = run_command("uv pip install -e .")
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print("✅ Dependencies installed")
    
    # Install openai
    print("📥 Installing OpenAI...")
    success, stdout, stderr = run_command("uv pip install openai typing-extensions")
    if not success:
        print(f"❌ Failed to install OpenAI: {stderr}")
        return False
    
    print("✅ All packages installed successfully")
    return True

if __name__ == "__main__":
    setup_uv_environment()