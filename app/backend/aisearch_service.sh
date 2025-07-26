#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="${SCRIPT_DIR}/../../venv"
APP_DIR="${SCRIPT_DIR}"

# Function to activate virtual environment
activate_venv() {
    source "${VENV_DIR}/bin/activate"
}

# Start the application
start() {
    echo "Starting AI Search backend service..."
    activate_venv
    cd "${APP_DIR}" && python app.py &
    echo $! > "${APP_DIR}/.pid"
    echo "Service started with PID: $(cat ${APP_DIR}/.pid)"
}

# Stop the application
stop() {
    if [ -f "${APP_DIR}/.pid" ]; then
        PID=$(cat "${APP_DIR}/.pid")
        if ps -p $PID > /dev/null; then
            echo "Stopping AI Search backend service (PID: $PID)..."
            kill $PID
            rm "${APP_DIR}/.pid"
            echo "Service stopped"
        else
            echo "Service is not running"
            rm "${APP_DIR}/.pid"
        fi
    else
        echo "PID file not found. Service may not be running."
    fi
}

# Restart the application
restart() {
    stop
    sleep 2
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
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 