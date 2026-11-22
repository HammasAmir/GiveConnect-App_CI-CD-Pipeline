
#!/bin/bash
set -e

APP_DIR="/opt/giveconnect"

echo "Installing required system packages..."
sudo apt-get update
sudo apt-get install -y python3-venv unzip

echo "Extracting GiveConnect application..."
sudo mkdir -p "$APP_DIR"
sudo unzip -o /tmp/giveconnect.zip -d "$APP_DIR"

echo "Setting application permissions..."
sudo chown -R ubuntu:ubuntu "$APP_DIR"

echo "Creating Python virtual environment..."
sudo -u ubuntu python3 -m venv "$APP_DIR/.venv"

echo "Installing Python dependencies..."
sudo -u ubuntu "$APP_DIR/.venv/bin/pip" install --upgrade pip
sudo -u ubuntu "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "Creating application service..."
sudo tee /etc/systemd/system/giveconnect.service > /dev/null <<'EOF'
[Unit]
Description=GiveConnect Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/giveconnect
ExecStart=/opt/giveconnect/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "Starting GiveConnect..."
sudo systemctl daemon-reload
sudo systemctl enable giveconnect
sudo systemctl restart giveconnect

echo "GiveConnect deployment completed!"
