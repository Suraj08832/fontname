#!/bin/bash
# Exit on error
set -e

echo "Cleaning up any existing processes..."
# Try to find and kill any existing Python processes (safely)
pkill -f "python bot.py" || echo "No existing processes found to clean up"

# Wait a bit to ensure processes are terminated
sleep 3

echo "Starting Telegram Bot..."
python bot.py 