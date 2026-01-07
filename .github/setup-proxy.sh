#!/bin/bash
# Automated setup script for sandbox-ubuntu proxy configuration

set -e

echo "🚀 Setting up sandbox-ubuntu EC2 instance as HTTP proxy for Databricks..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Squid
echo "🔧 Installing Squid proxy server..."
sudo apt install squid -y

# Backup original config
sudo cp /etc/squid/squid.conf /etc/squid/squid.conf.backup

# Create optimized Squid configuration
echo "⚙️ Configuring Squid for GitHub Actions..."
sudo tee /etc/squid/squid.conf > /dev/null <<'EOF'
# Squid HTTP Proxy Configuration for GitHub Actions → Databricks
# Optimized for security and performance

# Listen on port 3128
http_port 3128

# GitHub Actions IP ranges (updated regularly)
acl github_actions src 4.175.0.0/16
acl github_actions src 13.64.0.0/16
acl github_actions src 20.135.0.0/16
acl github_actions src 135.232.0.0/16
acl github_actions src 172.183.0.0/16
acl github_actions src 172.184.0.0/16

# Databricks domains
acl databricks dstdomain .databricks.com
acl databricks dstdomain .cloud.databricks.com
acl databricks dstdomain dbc-0c2248b3-6656.cloud.databricks.com

# AWS services (for Secrets Manager, etc.)
acl aws_services dstdomain .amazonaws.com

# Standard ports
acl SSL_ports port 443
acl Safe_ports port 80
acl Safe_ports port 443
acl CONNECT method CONNECT

# Access control rules
http_access allow github_actions databricks
http_access allow github_actions aws_services
http_access allow CONNECT SSL_ports github_actions
http_access deny all

# Security settings
forwarded_for delete
via off
request_header_access X-Forwarded-For deny all
request_header_access Via deny all
request_header_access Cache-Control deny all

# Performance settings
cache deny all
memory_pools off

# Logging
access_log /var/log/squid/access.log squid
cache_log /var/log/squid/cache.log
logfile_rotate 10

# Timeouts
connect_timeout 30 seconds
request_timeout 60 seconds

# Error pages
error_directory /usr/share/squid/errors/English
EOF

# Set proper permissions
sudo chown proxy:proxy /etc/squid/squid.conf
sudo chmod 640 /etc/squid/squid.conf

# Create log directory if not exists
sudo mkdir -p /var/log/squid
sudo chown proxy:proxy /var/log/squid

# Test configuration
echo "🔍 Testing Squid configuration..."
sudo squid -k parse

# Start and enable Squid
echo "🚀 Starting Squid proxy service..."
sudo systemctl start squid
sudo systemctl enable squid

# Wait for service to start
sleep 5

# Check status
if sudo systemctl is-active --quiet squid; then
    echo "✅ Squid proxy is running successfully!"
else
    echo "❌ Failed to start Squid proxy"
    sudo systemctl status squid
    exit 1
fi

# Get instance metadata
echo "📋 Instance Information:"
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)

echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Private IP: $PRIVATE_IP"

# Test proxy locally
echo "🧪 Testing proxy connection..."
if curl -x http://localhost:3128 -s --connect-timeout 10 https://www.google.com > /dev/null; then
    echo "✅ Proxy is working correctly!"
else
    echo "⚠️ Proxy test failed - check configuration"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📝 Next Steps:"
echo "1. Add these GitHub Secrets:"
echo "   PROXY_HOST=$PUBLIC_IP"
echo "   PROXY_PORT=3128"
echo ""
echo "2. Whitelist this IP in Databricks:"
echo "   IP Address: $PUBLIC_IP/32"
echo ""
echo "3. Monitor proxy logs:"
echo "   sudo tail -f /var/log/squid/access.log"
echo ""
echo "4. Check proxy status:"
echo "   sudo systemctl status squid"