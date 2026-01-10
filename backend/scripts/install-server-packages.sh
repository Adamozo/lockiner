#!/bin/bash
#
# Server Setup Script for Debian 12/13
# Installs: Docker (with Compose plugin), UFW, Git, Nginx
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

log_info "Starting server setup for Debian 12/13..."

# Update system packages
log_info "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install prerequisites
log_info "Installing prerequisites..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common

# ============================================
# Install Git
# ============================================
log_info "Installing Git..."
apt-get install -y git
git --version
log_info "Git installed successfully"

# ============================================
# Install Docker with Compose Plugin
# ============================================
log_info "Installing Docker..."

# Remove old Docker versions if present
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update apt and install Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Verify installation
docker --version
docker compose version
log_info "Docker with Compose plugin installed successfully"

# Add current sudo user to docker group (if SUDO_USER is set)
if [ -n "$SUDO_USER" ]; then
    log_info "Adding user '$SUDO_USER' to docker group..."
    usermod -aG docker "$SUDO_USER"
    log_info "User added to docker group. Log out and back in for changes to take effect."
fi

# ============================================
# Install Nginx
# ============================================
log_info "Installing Nginx..."
apt-get install -y nginx

# Enable and start Nginx
systemctl enable nginx
systemctl start nginx

nginx -v
log_info "Nginx installed successfully"

# ============================================
# Install and Configure UFW
# ============================================
log_info "Installing UFW..."
apt-get install -y ufw

# Configure UFW rules
log_info "Configuring UFW firewall rules..."

# Reset UFW to defaults
ufw --force reset

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (important - don't lock yourself out!)
ufw allow ssh
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow Nginx profiles
ufw allow 'Nginx Full'

# Enable UFW
log_info "Enabling UFW..."
ufw --force enable

# Show UFW status
ufw status verbose
log_info "UFW installed and configured successfully"

# ============================================
# Create directory structure for Nginx
# ============================================
log_info "Setting up Nginx directory structure..."
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Ensure sites-enabled is included in nginx.conf
if ! grep -q "include /etc/nginx/sites-enabled" /etc/nginx/nginx.conf; then
    log_info "Adding sites-enabled include to nginx.conf..."
    sed -i '/http {/a \    include /etc/nginx/sites-enabled/*;' /etc/nginx/nginx.conf
fi

# ============================================
# Summary
# ============================================
echo ""
echo "============================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "============================================"
echo ""
echo "Installed packages:"
echo "  - Git: $(git --version)"
echo "  - Docker: $(docker --version)"
echo "  - Docker Compose: $(docker compose version)"
echo "  - Nginx: $(nginx -v 2>&1)"
echo "  - UFW: $(ufw version | head -n1)"
echo ""
echo "UFW Status:"
ufw status
echo ""
echo "Next steps:"
echo "  1. Log out and back in for docker group changes to take effect"
echo "  2. Run the certbot setup script for HTTPS certificates"
echo "  3. Configure your Nginx sites in /etc/nginx/sites-available/"
echo ""
