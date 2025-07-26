#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SERVICE_FILE="${SCRIPT_DIR}/aisearch-backend.service"
SERVICE_NAME="aisearch-backend.service"

# Check if running as root/sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Copy service file to systemd directory
echo "Installing service file to /etc/systemd/system/${SERVICE_NAME}"
cp "${SERVICE_FILE}" "/etc/systemd/system/${SERVICE_NAME}"

# Reload systemd to recognize the new service
echo "Reloading systemd daemon"
systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling service to start on boot"
systemctl enable "${SERVICE_NAME}"

echo "Service installation complete!"
echo "You can now manage the service with these commands:"
echo "  sudo systemctl start ${SERVICE_NAME}"
echo "  sudo systemctl stop ${SERVICE_NAME}"
echo "  sudo systemctl restart ${SERVICE_NAME}"
echo "  sudo systemctl status ${SERVICE_NAME}"

# Ask if the user wants to start the service now
read -p "Do you want to start the service now? (y/n): " START_SERVICE
if [[ "${START_SERVICE}" =~ ^[Yy]$ ]]; then
  echo "Starting service..."
  systemctl start "${SERVICE_NAME}"
  systemctl status "${SERVICE_NAME}"
fi

exit 0 