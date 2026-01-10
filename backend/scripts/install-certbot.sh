#!/bin/bash
#
# Certbot Installation and Setup Script for Debian 12/13
# Installs Certbot with Nginx plugin for free Let's Encrypt SSL certificates
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

# Get domain and email from arguments or prompt
DOMAIN=${1:-""}
EMAIL=${2:-""}

if [ -z "$DOMAIN" ]; then
    read -p "Enter your domain name (e.g., example.com): " DOMAIN
fi

if [ -z "$EMAIL" ]; then
    read -p "Enter your email for certificate notifications: " EMAIL
fi

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    log_error "Domain and email are required"
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 lockiner.com admin@lockiner.com"
    exit 1
fi

log_info "Starting Certbot installation..."

# ============================================
# Install Certbot
# ============================================
log_info "Installing Certbot and Nginx plugin..."

# Install snapd (recommended method for Certbot)
apt-get update
apt-get install -y snapd

# Ensure snapd is up to date
snap install core
snap refresh core

# Remove any OS-packaged certbot to avoid conflicts
apt-get remove -y certbot 2>/dev/null || true

# Install Certbot via snap
snap install --classic certbot

# Create symlink for certbot command
ln -sf /snap/bin/certbot /usr/bin/certbot

# Verify installation
certbot --version
log_info "Certbot installed successfully"

# ============================================
# Obtain SSL Certificate
# ============================================
log_info "Obtaining SSL certificate for $DOMAIN..."

# Check if Nginx config exists for the domain
if [ ! -f "/etc/nginx/sites-available/$DOMAIN" ]; then
    log_warn "No Nginx config found for $DOMAIN"
    log_info "Creating a basic Nginx config first..."

    # Create a basic config for certbot to work with
    cat > "/etc/nginx/sites-available/$DOMAIN" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    root /var/www/$DOMAIN/html;
    index index.html index.htm;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

    # Create web root directory
    mkdir -p /var/www/$DOMAIN/html
    echo "<html><body><h1>Welcome to $DOMAIN</h1></body></html>" > /var/www/$DOMAIN/html/index.html
    chown -R www-data:www-data /var/www/$DOMAIN

    # Enable the site
    ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

    # Test and reload nginx
    nginx -t
    systemctl reload nginx
fi

# Obtain certificate using Nginx plugin
log_info "Running Certbot to obtain certificate..."
certbot --nginx \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --redirect

# ============================================
# Setup Auto-Renewal
# ============================================
log_info "Setting up automatic certificate renewal..."

# Test renewal process
certbot renew --dry-run

# Certbot snap automatically installs a systemd timer for renewal
# Verify it's active
if systemctl list-timers | grep -q certbot; then
    log_info "Certbot auto-renewal timer is active"
else
    log_warn "Setting up cron job for auto-renewal..."
    # Fallback to cron if systemd timer not present
    (crontab -l 2>/dev/null | grep -v certbot; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
fi

# ============================================
# Summary
# ============================================
echo ""
echo "============================================"
echo -e "${GREEN}Certbot Setup Complete!${NC}"
echo "============================================"
echo ""
echo "SSL Certificate obtained for:"
echo "  - $DOMAIN"
echo "  - www.$DOMAIN"
echo ""
echo "Certificate files location:"
echo "  - Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "  - Private Key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo ""
echo "Auto-renewal is configured. Certificates will renew automatically."
echo ""
echo "Useful commands:"
echo "  - Check certificate status: certbot certificates"
echo "  - Test renewal: certbot renew --dry-run"
echo "  - Force renewal: certbot renew --force-renewal"
echo ""
