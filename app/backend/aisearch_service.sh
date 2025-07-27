#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="${SCRIPT_DIR}/.venv"
APP_DIR="${SCRIPT_DIR}"
LOG_FILE="${APP_DIR}/service.log"
CELERY_LOG_FILE="${APP_DIR}/celery.log"

# Function to activate virtual environment
activate_venv() {
    if [ -f "${VENV_DIR}/bin/activate" ]; then
        source "${VENV_DIR}/bin/activate"
    else
        echo "Warning: Virtual environment not found at ${VENV_DIR}"
        # Check if Python is available in the system
        if command -v python3 &> /dev/null; then
            echo "Using system Python instead"
        else
            echo "Error: Neither virtual environment nor system Python is available"
            exit 1
        fi
    fi
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

# Start the Celery worker
start_celery() {
    echo "Starting Celery worker..."
    activate_venv
    cd "${APP_DIR}" && celery -A tasks worker --loglevel=info > "${CELERY_LOG_FILE}" 2>&1 &
    echo $! > "${APP_DIR}/.celery_pid"
    echo "Celery worker started with PID: $(cat ${APP_DIR}/.celery_pid)"
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

# Stop the Celery worker
stop_celery() {
    if [ -f "${APP_DIR}/.celery_pid" ]; then
        PID=$(cat "${APP_DIR}/.celery_pid")
        if ps -p $PID > /dev/null; then
            echo "Stopping Celery worker (PID: $PID)..."
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
            rm "${APP_DIR}/.celery_pid"
            echo "Celery worker stopped"
        else
            echo "Celery worker is not running"
            rm "${APP_DIR}/.celery_pid"
        fi
    else
        echo "Celery PID file not found. Checking for any running celery processes..."
        # Try to find and kill any celery processes
        CELERY_PIDS=$(ps aux | grep "celery -A tasks worker" | grep -v grep | awk '{print $2}')
        if [ ! -z "$CELERY_PIDS" ]; then
            echo "Found celery processes, stopping them..."
            for pid in $CELERY_PIDS; do
                echo "Killing celery process with PID: $pid"
                kill -9 $pid
            done
            echo "Celery processes killed"
        else
            echo "No celery processes found"
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

# Restart the Celery worker
restart_celery() {
    stop_celery
    sleep 2
    start_celery
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
    
    if [ -f "${APP_DIR}/.celery_pid" ]; then
        PID=$(cat "${APP_DIR}/.celery_pid")
        if ps -p $PID > /dev/null; then
            echo "Celery worker is running with PID: $PID"
        else
            echo "Celery worker is not running (stale PID file)"
        fi
    else
        echo "Celery worker is not running"
    fi
}

# View logs
logs() {
    if [ "$1" == "celery" ]; then
        if [ -f "${CELERY_LOG_FILE}" ]; then
            if [ "$2" == "follow" ]; then
                tail -f "${CELERY_LOG_FILE}"
            else
                cat "${CELERY_LOG_FILE}"
            fi
        else
            echo "Celery log file not found"
        fi
    else
        if [ -f "${LOG_FILE}" ]; then
            if [ "$1" == "follow" ]; then
                tail -f "${LOG_FILE}"
            else
                cat "${LOG_FILE}"
            fi
        else
            echo "Log file not found"
        fi
    fi
}

# Start all services
start_all() {
    start
    start_celery
}

# Stop all services
stop_all() {
    stop
    stop_celery
}

# Restart all services
restart_all() {
    restart
    restart_celery
}

# Parse command line arguments
case "$1" in
    start)
        if [ "$2" == "celery" ]; then
            start_celery
        elif [ "$2" == "all" ]; then
            start_all
        else
            start
        fi
        ;;
    stop)
        if [ "$2" == "celery" ]; then
            stop_celery
        elif [ "$2" == "all" ]; then
            stop_all
        else
            stop
        fi
        ;;
    restart)
        if [ "$2" == "celery" ]; then
            restart_celery
        elif [ "$2" == "all" ]; then
            restart_all
        else
            restart
        fi
        ;;
    status)
        status
        ;;
    logs)
        logs "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs} [celery|all] [follow]"
        echo "Examples:"
        echo "  $0 start         # Start backend service"
        echo "  $0 start celery  # Start celery worker"
        echo "  $0 start all     # Start both services"
        echo "  $0 logs          # View backend logs"
        echo "  $0 logs celery   # View celery logs"
        echo "  $0 logs follow   # View backend logs and follow"
        echo "  $0 logs celery follow # View celery logs and follow"
        exit 1
        ;;
esac

exit 0 