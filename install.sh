#!/bin/bash

set -e

echo "==> Updating system and installing dependencies..."
apt update && apt install -y python3 python3-pip git curl

echo "==> Cloning repo to /opt/email-verify..."
git clone https://github.com/emailengineer/email-verify.git /opt/email-verify

echo "==> Installing Python packages..."
pip3 install -r /opt/email-verify/requirements.txt

echo "==> Setting up systemd service..."
cp /opt/email-verify/smtp-verifier.service /etc/systemd/system/smtp-verifier.service
systemctl daemon-reload
systemctl enable smtp-verifier
systemctl start smtp-verifier

echo "✅ SMTP Verifier API is now running on port 8080"
