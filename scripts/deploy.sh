#!/bin/bash

# Configuration
APP_USER="dorsal"
BASE_DIR="/home/$APP_USER/dorsal-app"
API_DIR="$BASE_DIR/api"
WEB_DIR="$BASE_DIR/web"
SCRIPTS_DIR="$BASE_DIR/scripts"

API_SERVICE="dorsal-api.service"
WEB_SERVICE="dorsal-web.service"

echo "Starting deployment for Dorsal..."

# Root check
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run with sudo."
    exit 1
fi

# Ensure user exists
if ! id "$APP_USER" &>/dev/null; then
    echo "User $APP_USER not found. Creating user..."
    useradd -m -s /bin/bash "$APP_USER"
    usermod -aG www-data "$APP_USER"
    chmod 711 /home/$APP_USER
fi

# Synchronize service file
echo "Installing service files to systemd..."
for SERVICE in "$API_SERVICE" "$WEB_SERVICE"; do
    if [ -f "$SCRIPTS_DIR/$SERVICE" ]; then
        # Copying is safer than linking on some systems to avoid permission issues
        cp "$SCRIPTS_DIR/$SERVICE" "/etc/systemd/system/$SERVICE"
        chmod 644 "/etc/systemd/system/$SERVICE"
    else
        echo "Warning: $SERVICE not found in $SCRIPTS_DIR"
    fi
done

# Update API (Python)
echo "Updating API dependencies..."
sudo -u "$APP_USER" bash <<EOF
    cd "$API_DIR"
    [ ! -d "venv" ] && python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    [ -f "requirements.txt" ] && pip install -r requirements.txt
    pip install gunicorn
EOF

# Update Web (Node.js)
echo "Updating Web dependencies..."
sudo -u "$APP_USER" bash <<EOF
    cd "$WEB_DIR"
    if command -v npm >/dev/null 2>&1; then
        npm install --omit=dev --no-audit --no-fund
    else
        echo "Error: npm not found. Install nodejs/npm first."
        exit 1
    fi
EOF

# Restart Services
echo "Reloading systemd and restarting services..."
systemctl daemon-reload

for SERVICE in "$API_SERVICE" "$WEB_SERVICE"; do
    systemctl enable "$SERVICE"
    systemctl restart "$SERVICE"
    echo "Service $SERVICE: $(systemctl is-active $SERVICE)"
done

echo "Deployment complete."