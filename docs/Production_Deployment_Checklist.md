# Production Deployment Checklist for WebTics

Complete checklist for deploying WebTics to production with security best practices.

---

## Pre-Deployment

### 1. Code Quality ✓

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Code coverage ≥80% (`pytest --cov=app`)
- [ ] No linting errors (`ruff check app/`)
- [ ] Code formatted (`black app/ --check`)
- [ ] Security scan clean (`bandit -r app/`)
- [ ] Type checking passed (`mypy app/`)
- [ ] No critical TODOs remaining

**Verify:**
```bash
cd backend
bash scripts/code_quality_check.sh
```

---

### 2. Secrets Management ✓

- [ ] Generated strong secrets (`./scripts/generate_secrets.sh`)
- [ ] API key documented and stored securely
- [ ] Database password is strong (32+ characters)
- [ ] SECRET_KEY is cryptographically random
- [ ] WITHDRAWAL_SECRET_KEY is unique
- [ ] `.env` file never committed to git
- [ ] Secrets stored in secure vault (optional: AWS Secrets Manager, HashiCorp Vault)

**Generate Production Secrets:**
```bash
chmod +x scripts/generate_secrets.sh
./scripts/generate_secrets.sh
# Save API key securely!
```

---

### 3. Environment Configuration ✓

**Update `.env` file:**

```bash
# Environment
ENVIRONMENT=production

# Database
POSTGRES_USER=webtics
POSTGRES_PASSWORD=<strong_random_password_from_generate_secrets>
POSTGRES_DB=webtics
DATABASE_URL=postgresql://webtics:<password>@db:5432/webtics

# API Security
WEBTICS_API_KEY=<api_key_from_generate_secrets>
SECRET_KEY=<secret_key_from_generate_secrets>
WITHDRAWAL_SECRET_KEY=<withdrawal_key_from_generate_secrets>

# CORS (update with your actual domain)
ALLOWED_ORIGINS=https://webtics.yourdomain.com

# Logging
LOG_LEVEL=INFO
LOG_DIR=/var/log/webtics
ENABLE_FILE_LOGGING=false  # Use Docker logs (stdout)
```

**Verify:**
- [ ] All secrets are unique and strong
- [ ] `ALLOWED_ORIGINS` updated with production domain
- [ ] `ENVIRONMENT=production`
- [ ] No default/development values

---

### 4. HTTPS/SSL Certificate ✓

**Option A: Let's Encrypt (Free)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d webtics.yourdomain.com

# Auto-renewal (cron)
sudo systemctl enable certbot.timer
```

**Option B: Custom Certificate**

```bash
# Place certificate files
/etc/ssl/certs/webtics.crt
/etc/ssl/private/webtics.key

# Update nginx config
ssl_certificate /etc/ssl/certs/webtics.crt;
ssl_certificate_key /etc/ssl/private/webtics.key;
```

- [ ] SSL certificate obtained
- [ ] Certificate valid for domain
- [ ] Auto-renewal configured
- [ ] Certificate expiry monitored

---

### 5. Firewall Configuration ✓

**UFW (Uncomplicated Firewall):**

```bash
# Enable firewall
sudo ufw enable

# Allow SSH (IMPORTANT: Do this first!)
sudo ufw allow 22/tcp

# Allow HTTP (for Let's Encrypt challenges)
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Deny all other ports
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

- [ ] Firewall enabled
- [ ] Only ports 22, 80, 443 open
- [ ] SSH access confirmed before enabling
- [ ] Database port (5432) NOT exposed to internet

---

### 6. Database Backup ✓

**Automated Backup Script:**

```bash
#!/bin/bash
# /opt/webtics/backup.sh

BACKUP_DIR="/backups/webtics"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="webtics"
DB_USER="webtics"
DB_PASSWORD=$(grep POSTGRES_PASSWORD /opt/webtics/.env | cut -d'=' -f2)

# Create backup
PGPASSWORD=$DB_PASSWORD pg_dump -U $DB_USER -h localhost $DB_NAME | \
  gzip > $BACKUP_DIR/webtics_$DATE.sql.gz

# Delete backups older than 30 days
find $BACKUP_DIR -name "webtics_*.sql.gz" -mtime +30 -delete

# Optional: Upload to S3
# aws s3 cp $BACKUP_DIR/webtics_$DATE.sql.gz s3://your-bucket/webtics-backups/
```

**Cron Job (Daily at 2am):**
```bash
sudo crontab -e

# Add line:
0 2 * * * /opt/webtics/backup.sh >> /var/log/webtics/backup.log 2>&1
```

- [ ] Backup script created and tested
- [ ] Cron job configured
- [ ] Backup directory has sufficient space
- [ ] Restore tested successfully
- [ ] Off-site backup configured (optional: S3, rsync)

---

### 7. Monitoring & Alerting ✓

**Health Check Monitoring:**

```bash
# Simple cron health check
*/5 * * * * curl -f https://webtics.yourdomain.com/health || echo "WebTics health check failed" | mail -s "WebTics Alert" admin@yourdomain.com
```

**Log Monitoring:**

```bash
# Watch for errors
tail -f /var/log/webtics/error.log

# Watch for security events
tail -f /var/log/webtics/security.log | grep "auth_failure\|rate_limit_exceeded"
```

- [ ] Health check endpoint accessible
- [ ] Error log monitoring configured
- [ ] Security event alerting configured
- [ ] Uptime monitoring (optional: UptimeRobot, Pingdom)
- [ ] Log aggregation (optional: ELK, Splunk)

---

## Deployment

### 8. Server Setup ✓

**System Requirements:**
- Ubuntu 22.04 LTS (recommended)
- 2-4 CPU cores
- 4-8GB RAM
- 100-500GB SSD storage
- Fixed IP address or domain

**Install Dependencies:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Install Nginx
sudo apt install nginx

# Verify installations
docker --version
docker compose version
nginx -v
```

- [ ] System updated
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] Nginx installed
- [ ] User added to docker group

---

### 9. Deploy Application ✓

```bash
# Create application directory
sudo mkdir -p /opt/webtics
sudo chown $USER:$USER /opt/webtics

# Clone repository
cd /opt/webtics
git clone https://github.com/SimonMcCallum/WebTics.git .

# Copy production .env
cp /path/to/secure/.env .env

# Build and start
docker compose up -d

# Check logs
docker compose logs -f
```

- [ ] Application files deployed
- [ ] `.env` file in place
- [ ] Docker containers running
- [ ] Database initialized
- [ ] Backend accessible on localhost:8013

**Verify:**
```bash
docker ps  # Should show webtics_backend and webtics_db
curl http://localhost:8013/health  # Should return 200
```

---

### 10. Nginx Reverse Proxy ✓

**Create config:** `/etc/nginx/sites-available/webtics`

```nginx
# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name webtics.yourdomain.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name webtics.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/webtics.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/webtics.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to backend
    location / {
        proxy_pass http://localhost:8013;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Logging
    access_log /var/log/nginx/webtics_access.log;
    error_log /var/log/nginx/webtics_error.log;
}
```

**Enable and test:**

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/webtics /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Enable on boot
sudo systemctl enable nginx
```

- [ ] Nginx config created
- [ ] Config syntax validated
- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] Security headers present

**Verify:**
```bash
curl -I https://webtics.yourdomain.com/health
# Should show: HTTP/2 200, security headers
```

---

## Post-Deployment

### 11. Security Verification ✓

**SSL Test:**
```bash
# Test SSL configuration
curl -I https://webtics.yourdomain.com/
# Check for: Strict-Transport-Security, X-Frame-Options

# External SSL test
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=webtics.yourdomain.com
# Target: A+ rating
```

**Security Headers:**
```bash
curl -I https://webtics.yourdomain.com/ | grep -E "Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options"
```

**Port Scan:**
```bash
nmap -p- webtics.yourdomain.com
# Should only show: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

- [ ] SSL Labs: A+ rating
- [ ] Security headers present
- [ ] Only required ports open
- [ ] No database port exposed

---

### 12. Functional Testing ✓

**API Tests:**

```bash
# Health check
curl https://webtics.yourdomain.com/health

# Create session (should require API key in production)
curl -X POST https://webtics.yourdomain.com/api/v1/sessions \
  -H "X-API-Key: $WEBTICS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"unique_id": "prod_test_001", "build_number": "1.0.0"}'

# Log event
curl -X POST https://webtics.yourdomain.com/api/v1/events?play_session_id=1 \
  -H "X-API-Key: $WEBTICS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"event_type": 100, "magnitude": 123.45}'
```

- [ ] Health endpoint accessible
- [ ] API key required (401 without key)
- [ ] Session creation works
- [ ] Event logging works
- [ ] Rate limiting works (test 101 requests)

---

### 13. Monitoring Setup ✓

**Create monitoring script:** `/opt/webtics/monitor.sh`

```bash
#!/bin/bash
# Monitor WebTics health and send alerts

HEALTH_URL="https://webtics.yourdomain.com/health"
ALERT_EMAIL="admin@yourdomain.com"

# Check health
if ! curl -sf "$HEALTH_URL" > /dev/null; then
    echo "WebTics health check failed at $(date)" | mail -s "ALERT: WebTics Down" "$ALERT_EMAIL"
fi

# Check disk space
DISK_USAGE=$(df /opt/webtics | tail -1 | awk '{print $5}' | tr -d '%')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage at ${DISK_USAGE}% on $(date)" | mail -s "ALERT: WebTics Disk Space" "$ALERT_EMAIL"
fi

# Check Docker containers
if [ $(docker ps | grep webtics | wc -l) -lt 2 ]; then
    echo "WebTics containers not running at $(date)" | mail -s "ALERT: WebTics Containers" "$ALERT_EMAIL"
fi
```

**Cron (every 5 minutes):**
```bash
*/5 * * * * /opt/webtics/monitor.sh >> /var/log/webtics/monitor.log 2>&1
```

- [ ] Monitoring script created
- [ ] Cron job configured
- [ ] Email alerts working
- [ ] Disk space monitored
- [ ] Container health monitored

---

### 14. Documentation ✓

- [ ] API key distributed to authorized clients
- [ ] Deployment documented (date, version, changes)
- [ ] Backup/restore procedures documented
- [ ] Incident response plan created
- [ ] Team trained on monitoring and alerts

**Create runbook:** `/opt/webtics/RUNBOOK.md`

```markdown
# WebTics Production Runbook

## Deployment Info
- Deployed: 2026-02-16
- Version: 0.1.0
- Domain: https://webtics.yourdomain.com

## Key Files
- Application: /opt/webtics/
- Logs: /var/log/webtics/
- Backups: /backups/webtics/
- Nginx: /etc/nginx/sites-available/webtics

## Common Operations

### Restart Application
docker-compose -f /opt/webtics/docker-compose.yml restart

### View Logs
docker-compose -f /opt/webtics/docker-compose.yml logs -f
tail -f /var/log/webtics/error.log

### Restore Database
gunzip < /backups/webtics/backup_YYYYMMDD.sql.gz | docker exec -i webtics_db psql -U webtics -d webtics

### Update Application
cd /opt/webtics && git pull && docker-compose up -d --build

## Contacts
- Admin: admin@yourdomain.com
- On-call: +64 21 XXX XXXX
```

---

## Final Checklist

### Pre-Go-Live

- [ ] All tests passing
- [ ] Secrets generated and secured
- [ ] HTTPS configured with A+ SSL rating
- [ ] Firewall enabled (ports 22, 80, 443 only)
- [ ] Database backups automated and tested
- [ ] Monitoring and alerting configured
- [ ] Nginx reverse proxy configured
- [ ] Environment set to production
- [ ] API keys distributed securely

### Go-Live

- [ ] DNS updated to point to server
- [ ] Application accessible via HTTPS
- [ ] HTTP redirects to HTTPS working
- [ ] API endpoints functional
- [ ] Rate limiting working
- [ ] Authentication required
- [ ] Logs being written

### Post-Go-Live

- [ ] Monitor logs for 24 hours
- [ ] Test backup/restore
- [ ] Verify monitoring alerts
- [ ] Document any issues
- [ ] Team briefed on operations

---

## Maintenance

### Daily
- Check error logs: `tail /var/log/webtics/error.log`
- Verify backups: `ls -lh /backups/webtics/ | tail -5`

### Weekly
- Review security logs: `grep "auth_failure\|rate_limit" /var/log/webtics/security.log`
- Check disk space: `df -h /opt/webtics`
- Update packages: `sudo apt update && sudo apt upgrade`

### Monthly
- Test backup restore
- Review API usage
- Rotate logs if needed
- Security audit

### Quarterly
- Update dependencies
- Security penetration test
- Disaster recovery drill
- Review and update documentation

---

**Status:** Production Ready ✅

**Last Updated:** February 16, 2026
