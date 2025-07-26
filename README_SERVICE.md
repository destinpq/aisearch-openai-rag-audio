# AI Search OpenAI RAG Audio Backend Service

This document explains how to deploy and manage the AI Search backend service.

## Option 1: Using the Shell Script (Manual Management)

The shell script provides a simple way to start, stop, and manage the service without system integration.

```bash
# Navigate to the backend directory
cd app/backend

# Start the service
./aisearch_service.sh start

# Check service status
./aisearch_service.sh status

# Stop the service
./aisearch_service.sh stop

# Restart the service
./aisearch_service.sh restart
```

This approach is useful for development or temporary deployments.

## Option 2: Using Systemd Service (Recommended for Production)

The systemd service provides automatic startup on boot, restart on failure, and better system integration.

### Installation

```bash
# Run the setup script with sudo
sudo ./setup_service.sh
```

### Managing the Service

```bash
# Start the service
sudo systemctl start aisearch-backend.service

# Stop the service
sudo systemctl stop aisearch-backend.service

# Restart the service
sudo systemctl restart aisearch-backend.service

# Check service status
sudo systemctl status aisearch-backend.service

# View service logs
sudo journalctl -u aisearch-backend.service

# View live logs
sudo journalctl -u aisearch-backend.service -f
```

### Uninstalling the Service

If you need to remove the service:

```bash
sudo systemctl stop aisearch-backend.service
sudo systemctl disable aisearch-backend.service
sudo rm /etc/systemd/system/aisearch-backend.service
sudo systemctl daemon-reload
``` 