#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="${SCRIPT_DIR}/../../.venv"
APP_DIR="${SCRIPT_DIR}"
LOG_FILE="${APP_DIR}/service.log"

# Function to activate virtual environment
activate_venv() {
    source "${VENV_DIR}/bin/activate"
}

# Start the application
start() {
    echo "Starting AI Search backend service..."
    # Check if port 8765 is already in use
    if lsof -i:8765 > /dev/null 2>&1; then
        echo "Port 8765 is already in use. Stopping existing process..."
        PORT_PID=$(lsof -t -i:8765 2>/dev/null)
        if [ ! -z "$PORT_PID" ]; then
            kill -9 $PORT_PID
            sleep 1
        fi
    fi
    activate_venv
    cd "${APP_DIR}" && python app.py > "${LOG_FILE}" 2>&1 &
    echo $! > "${APP_DIR}/.pid"
    echo "Service started with PID: $(cat ${APP_DIR}/.pid)"
    # Give it a moment to start up
    sleep 2
    if ! lsof -i:8765 > /dev/null 2>&1; then
        echo "Warning: Service started but not listening on port 8765"
    else
        echo "Service is running and listening on port 8765"
    fi
}

# Stop the application
stop() {
    if [ -f "${APP_DIR}/.pid" ]; then
        PID=$(cat "${APP_DIR}/.pid")
        if ps -p $PID > /dev/null; then
            echo "Stopping AI Search backend service (PID: $PID)..."
            kill $PID
            # Wait for up to 5 seconds for the process to exit gracefully
            for i in {1..5}; do
                if ! ps -p $PID > /dev/null; then
                    break
                fi
                sleep 1
            done
            # Force kill if still running
            if ps -p $PID > /dev/null; then
                echo "Process didn't exit gracefully, force killing..."
                kill -9 $PID
            fi
            rm "${APP_DIR}/.pid"
            echo "Service stopped"
        else
            echo "Service is not running"
            rm "${APP_DIR}/.pid"
        fi
    else
        echo "PID file not found. Checking for any running processes..."
        # Check if there's any process running on port 8765
        PORT_PID=$(lsof -t -i:8765 2>/dev/null)
        if [ ! -z "$PORT_PID" ]; then
            echo "Found process using port 8765 (PID: $PORT_PID), stopping it..."
            kill -9 $PORT_PID
            echo "Process killed"
        else
            echo "No process found using port 8765"
        fi
    fi
}

# Restart the application
restart() {
    stop
    sleep 2
    # Double check port is free before starting
    if lsof -i:8765 > /dev/null 2>&1; then
        echo "Port 8765 is still in use after stop. Force killing process..."
        lsof -t -i:8765 | xargs -r kill -9
        sleep 1
    fi
    start
}

# Check status of the application
status() {
    if [ -f "${APP_DIR}/.pid" ]; then
        PID=$(cat "${APP_DIR}/.pid")
        if ps -p $PID > /dev/null; then
            echo "Service is running with PID: $PID"
        else
            echo "Service is not running (stale PID file)"
        fi
    else
        echo "Service is not running"
    fi
}

# View logs
logs() {
    if [ -f "${LOG_FILE}" ]; then
        if [ "$1" == "follow" ]; then
            tail -f "${LOG_FILE}"
        else
            cat "${LOG_FILE}"
        fi
    else
        echo "Log file not found"
    fi
}

# Parse command line arguments
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [follow]}"
        exit 1
        ;;
esac

exit 0 