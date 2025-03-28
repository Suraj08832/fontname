#!/bin/bash
# Exit on error
set -e

# Enable debug mode
set -x

echo "=== Starting Font Bot Deployment ==="
echo "Current time: $(date)"
echo "Python version: $(python --version)"

echo "Cleaning up any existing processes..."
# Kill all Python processes running bot.py
pkill -9 -f "python.*bot.py" || echo "No existing processes found to clean up"

# Additional cleanup for any hanging processes
for pid in $(pgrep -f "python.*bot.py"); do
    kill -9 $pid 2>/dev/null || true
done

# Wait a bit to ensure processes are terminated
sleep 5

# Verify no bot processes are running
if pgrep -f "python.*bot.py" > /dev/null; then
    echo "Warning: Some bot processes are still running. Forcing cleanup..."
    pkill -9 -f "python.*bot.py"
    sleep 3
fi

echo "Starting Telegram Bot with auto-restart..."

# Set the maximum number of restart attempts
MAX_RESTARTS=5
restart_count=0
last_restart_time=0
MIN_RESTART_INTERVAL=30  # Minimum seconds between restarts

# Function to check if bot is running
check_bot_status() {
    if pgrep -f "python.*bot.py" > /dev/null; then
        echo "Bot process is running"
        return 0
    else
        echo "Bot process is not running"
        return 1
    fi
}

# Function to get bot logs
get_bot_logs() {
    if [ -f bot.log ]; then
        echo "=== Bot Logs ==="
        cat bot.log
        echo "=== End of Bot Logs ==="
    else
        echo "No bot.log file found"
    fi
}

# Function to check Python environment
check_python_env() {
    echo "Checking Python environment..."
    python -c "import telegram; print('python-telegram-bot version:', telegram.__version__)"
    python -c "import requests; print('requests version:', requests.__version__)"
    python -c "import sys; print('Python path:', sys.path)"
}

# Restart loop
while [ $restart_count -lt $MAX_RESTARTS ]; do
    current_time=$(date +%s)
    
    # Check if enough time has passed since last restart
    if [ $((current_time - last_restart_time)) -lt $MIN_RESTART_INTERVAL ]; then
        wait_time=$((MIN_RESTART_INTERVAL - (current_time - last_restart_time)))
        echo "Waiting $wait_time seconds before next restart attempt..."
        sleep $wait_time
    fi
    
    echo "=== Starting bot (attempt $((restart_count+1))/$MAX_RESTARTS) ==="
    echo "Current time: $(date)"
    
    # Check Python environment before starting
    check_python_env
    
    # Clean up any existing processes before starting
    pkill -9 -f "python.*bot.py" || true
    
    # Start the bot in the background and capture its PID
    # Use python -u to disable output buffering
    python -u bot.py > bot.log 2>&1 &
    BOT_PID=$!
    
    # Wait a few seconds to see if the bot starts properly
    sleep 5
    
    # Check if bot is running
    if check_bot_status; then
        echo "Bot started successfully with PID: $BOT_PID"
        echo "Waiting for logs to be generated..."
        sleep 2
        get_bot_logs
        
        # Monitor the bot for a while to ensure it stays running
        for i in {1..3}; do
            sleep 5
            if ! check_bot_status; then
                echo "Bot stopped unexpectedly after $((i*5)) seconds"
                get_bot_logs
                break
            fi
        done
    else
        echo "Bot failed to start properly"
        get_bot_logs
    fi
    
    # Update restart count and time
    restart_count=$((restart_count+1))
    last_restart_time=$(date +%s)
    
    # Only restart if we haven't reached the maximum
    if [ $restart_count -lt $MAX_RESTARTS ]; then
        echo "Bot exited unexpectedly. Waiting 10 seconds before restart..."
        sleep 10
    else
        echo "Maximum restart attempts reached. Please check logs for errors."
        get_bot_logs
        exit 1
    fi
done

echo "Bot process ended. Check logs for details." 