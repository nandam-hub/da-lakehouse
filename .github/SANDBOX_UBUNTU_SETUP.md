# Setup sandbox-ubuntu as HTTP Proxy

## Instance Details:
- **Name:** sandbox-ubuntu
- **Public IP:** 18.222.51.168
- **Purpose:** HTTP proxy for GitHub Actions → Databricks

## Quick Setup Commands:

### 1. SSH to sandbox-ubuntu:
```bash
ssh -i your-key.pem ubuntu@18.222.51.168
```

### 2. Run Setup Script:
```bash
# Install and configure Squid proxy
sudo apt update && sudo apt install squid -y

# Create Squid configuration
sudo tee /etc/squid/squid.conf > /dev/null <<EOF
# Squid HTTP Proxy for GitHub Actions → Databricks
http_port 3128

# GitHub Actions IP ranges
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

# AWS services
acl aws_services dstdomain .amazonaws.com

# Ports
acl SSL_ports port 443
acl CONNECT method CONNECT

# Access rules
http_access allow github_actions databricks
http_access allow github_actions aws_services
http_access allow CONNECT SSL_ports github_actions
http_access deny all

# Security
forwarded_for delete
via off
cache deny all

# Logging
access_log /var/log/squid/access.log squid
EOF

# Start Squid
sudo systemctl start squid
sudo systemctl enable squid
sudo systemctl status squid
```

### 3. Test Proxy:
```bash
# Test locally
curl -x http://localhost:3128 https://www.google.com

# Check logs
sudo tail -f /var/log/squid/access.log
```

## Required Actions:

### 1. Whitelist in Databricks:
- **Go to:** Databricks Admin Console → IP Access Lists
- **Add new list:**
  - **Name:** `sandbox-ubuntu-proxy`
  - **IP/CIDR:** `18.222.51.168/32`
  - **Type:** Allow
- **Enable the list**

### 2. Security Group (if needed):
```bash
# Allow inbound port 3128 from GitHub Actions IPs
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 3128 \
  --cidr 0.0.0.0/0
```

## Verification:

### Test from external:
```bash
# Test proxy from another machine
curl -x http://18.222.51.168:3128 https://dbc-0c2248b3-6656.cloud.databricks.com/health
```

### Monitor traffic:
```bash
# Watch proxy logs in real-time
sudo tail -f /var/log/squid/access.log

# Check proxy status
sudo systemctl status squid
```

## Workflow Configuration:

The workflow is now hardcoded to use:
- **Proxy Host:** 18.222.51.168
- **Proxy Port:** 3128

No GitHub secrets needed - the IP is directly configured in the workflow.

## Next Steps:

1. ✅ **Run setup commands** on sandbox-ubuntu
2. ✅ **Whitelist 18.222.51.168/32** in Databricks
3. ✅ **Test the workflow** - it should now bypass IP ACL restrictions

**The proxy will route all GitHub Actions traffic through sandbox-ubuntu to Databricks!**