#!/bin/bash

set -euo pipefail

log() {
    echo -e "\033[1;32m[INFO]\033[0m $1"
}

error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
    exit 1
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "'$1' command not found. Please install it and rerun this script."
    fi
}

log "Checking required commands..."
check_command curl
check_command git
check_command python3
check_command pip3
check_command systemctl

log "Updating system packages..."
apt update -y || error "Failed to update package list"
apt install -y python3 python3-pip git curl || error "Failed to install dependencies"

TARGET_DIR="/opt/email-verify"
REPO_URL="https://github.com/emailengineer/email-verify.git"

if [ -d "$TARGET_DIR" ]; then
    log "Directory $TARGET_DIR already exists. Pulling latest changes..."
    cd "$TARGET_DIR" && git pull origin main || error "Failed to update repository"
else
    log "Cloning repository into $TARGET_DIR..."
    git clone "$REPO_URL" "$TARGET_DIR" || error "Failed to clone repository"
fi

cd "$TARGET_DIR" || error "Failed to enter directory $TARGET_DIR"

log "Installing Python requirements..."
pip3 install -r requirements.txt || error "pip3 failed"

SERVICE_FILE="/etc/systemd/system/smtp-verifier.service"

if [ -f "$SERVICE_FILE" ]; then
    log "Service file already exists. Removing old version..."
    systemctl stop smtp-verifier || true
    rm "$SERVICE_FILE"
fi

log "Copying systemd service file..."
cp smtp-verifier.service "$SERVICE_FILE" || error "Failed to copy service file"

log "Reloading systemd daemon..."
systemctl daemon-reexec
systemctl daemon-reload

log "Enabling and starting the service..."
systemctl enable smtp-verifier || error "Failed to enable service"
systemctl start smtp-verifier || error "Failed to start service"

sleep 1
if systemctl is-active --quiet smtp-verifier; then
    log "✅ SMTP Verifier is now running at port 8080"
else
    error "Service failed to start. Check logs with: journalctl -u smtp-verifier -e"
fi
