#!/usr/bin/env python3
import os
import sys

def create_env_file():
    """Create .env file with bot token."""
    if os.path.exists('.env'):
        print("An .env file already exists.")
        overwrite = input("Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Setup aborted.")
            return False
    
    token = input("Enter your Telegram bot token: ")
    if not token:
        print("Token cannot be empty. Setup aborted.")
        return False
    
    with open('.env', 'w') as f:
        f.write(f"TOKEN={token}\n")
    
    print(".env file created successfully.")
    return True

def setup_project():
    """Setup the project for local development."""
    try:
        import dotenv
    except ImportError:
        print("Installing required packages...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")
    
    print("\nSetting up environment variables...")
    if not create_env_file():
        return
    
    print("\nSetup completed successfully!")
    print("You can now run the bot with: python bot.py")

if __name__ == "__main__":
    setup_project() 