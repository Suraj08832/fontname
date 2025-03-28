#!/bin/bash
# Exit on error
set -e

echo "Cleaning up any existing processes..."
# Try to find and kill any existing Python processes (safely)
pkill -f "python bot.py" || echo "No existing processes found to clean up"

# Wait a bit to ensure processes are terminated
sleep 3

echo "Starting Telegram Bot with auto-restart..."

# Set the maximum number of restart attempts
MAX_RESTARTS=5
restart_count=0

# Restart loop
while [ $restart_count -lt $MAX_RESTARTS ]; do
    echo "Starting bot (attempt $((restart_count+1))/$MAX_RESTARTS)..."
    
    # Start the bot and capture its exit code
    python bot.py || true
    
    # Increment restart count
    restart_count=$((restart_count+1))
    
    # Only restart if we haven't reached the maximum
    if [ $restart_count -lt $MAX_RESTARTS ]; then
        echo "Bot exited unexpectedly. Restarting in 10 seconds..."
        sleep 10
    else
        echo "Maximum restart attempts reached. Please check logs for errors."
    fi
done

echo "Bot process ended. Check logs for details." 