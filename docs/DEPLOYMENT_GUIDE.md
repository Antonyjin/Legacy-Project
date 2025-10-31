# Deployment Guide

This guide covers deploying the GeneWeb application to various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Setup](#docker-setup)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows (WSL2)
- **Python**: 3.11+
- **OCaml**: 4.14+ (for legacy binary compatibility)
- **Disk Space**: 500MB+ (for application + databases)
- **Memory**: 2GB+ recommended

### Software Requirements
- Git
- Docker & Docker Compose (optional, for containerized deployment)
- pip (Python package manager)
- curl (for health checks)

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/Antonyjin/Legacy-Project.git
cd Legacy-Project
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file in project root:

```env
# Application
PORT=2317
FLASK_ENV=development
LOG_LEVEL=debug

# Database
DATABASE_PATH=./GeneWeb/bases

# Backend
BACKEND=ocaml  # or 'python' for migrated functions

# Logging
LOG_FILE=./logs/app.log
```

### 4. Start OCaml Backend

```bash
# Navigate to GeneWeb directory
cd GeneWeb

# Start gwd daemon on port 23179
./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &

# Verify it's running
curl http://localhost:23179/test

# Return to project root
cd ..
```

### 5. Run Application

```bash
# With OCaml backend
BACKEND=ocaml python -m python_app.app

# With Python backend (uses migrated functions)
BACKEND=python python -m python_app.app

# Access at http://localhost:2317
```

### 6. Verify Deployment

```bash
# Check application health
curl http://localhost:2317/health

# Check gwd
curl http://localhost:23179/test?p=Charles&n=Windsor

# View logs
tail -f logs/app.log
```

## Docker Setup

### Prerequisites
- Docker 20.10+
- Docker Compose 1.29+

### Single Container

#### Build Image

```bash
docker build -t geneweb:latest .
```

#### Run Container

```bash
docker run \
  -p 2317:2317 \
  -v $(pwd)/GeneWeb/bases:/app/bases \
  -v $(pwd)/logs:/app/logs \
  -e LOG_LEVEL=info \
  -e BACKEND=ocaml \
  geneweb:latest
```

#### Access Application

```bash
# Web interface
curl http://localhost:2317/health

# View logs
docker logs <container_id>
```

### Docker Compose

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  geneweb:
    build: .
    container_name: geneweb
    ports:
      - "2317:2317"
    volumes:
      - ./GeneWeb/bases:/app/bases
      - ./logs:/app/logs
    environment:
      PORT: 2317
      FLASK_ENV: production
      LOG_LEVEL: info
      BACKEND: ocaml
      DATABASE_PATH: /app/bases
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:2317/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s

  # Optional: Reverse proxy (nginx)
  nginx:
    image: nginx:alpine
    container_name: geneweb-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - geneweb
    restart: unless-stopped
```

#### Deploy with Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f geneweb

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

#### Environment File (.env)

Create `.env` file for docker-compose:

```env
# Compose
COMPOSE_PROJECT_NAME=geneweb

# Application
PORT=2317
FLASK_ENV=production
LOG_LEVEL=info
BACKEND=ocaml

# Database path (inside container)
DATABASE_PATH=/app/bases
```

## Production Deployment

### Deployment Options

Choose one of the following deployment targets:

#### Option 1: VPS (AWS, DigitalOcean, Linode)

```bash
# SSH into server
ssh ubuntu@your-server.com

# Clone repository
git clone https://github.com/Antonyjin/Legacy-Project.git
cd Legacy-Project

# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure systemd service
sudo tee /etc/systemd/system/geneweb.service > /dev/null <<EOF
[Unit]
Description=GeneWeb Application
After=network.target

[Service]
Type=simple
User=geneweb
WorkingDirectory=/home/geneweb/Legacy-Project
ExecStart=/home/geneweb/Legacy-Project/venv/bin/python -m python_app.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable geneweb
sudo systemctl start geneweb

# Check status
sudo systemctl status geneweb
```

#### Option 2: Heroku

```bash
# Install Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create geneweb-app

# Add buildpack
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set FLASK_ENV=production LOG_LEVEL=info

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Open app
heroku open
```

#### Option 3: AWS (ECS/Fargate)

```bash
# Build and push image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker build -t geneweb:latest .
docker tag geneweb:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/geneweb:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/geneweb:latest

# Create ECS task definition (geneweb-task.json)
# Deploy with CloudFormation or AWS Console
```

#### Option 4: Docker on VPS (Recommended)

```bash
# SSH into server
ssh ubuntu@your-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Clone and deploy
git clone https://github.com/Antonyjin/Legacy-Project.git
cd Legacy-Project

# Create .env file
cat > .env <<EOF
PORT=2317
FLASK_ENV=production
LOG_LEVEL=info
BACKEND=ocaml
DATABASE_PATH=/app/bases
EOF

# Start with docker-compose
docker-compose up -d

# Verify
curl http://localhost:2317/health
```

### SSL/HTTPS Setup

#### Using Let's Encrypt with nginx

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure nginx reverse proxy
sudo tee /etc/nginx/sites-available/geneweb > /dev/null <<EOF
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:2317;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://\$server_name\$request_uri;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/geneweb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Auto-renew certificates
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Environment Configuration

### Environment Variables

```env
# Flask
FLASK_ENV=production              # development, production
FLASK_DEBUG=0                      # Disable debug mode in production
SECRET_KEY=your-secret-key         # For session encryption

# Application
PORT=2317                          # Application port
LOG_LEVEL=info                     # debug, info, warning, error

# Database
DATABASE_PATH=/app/bases           # Path to GWB databases
DATABASE_TIMEOUT=30                # Connection timeout (seconds)

# Backend
BACKEND=ocaml                      # ocaml or python

# Logging
LOG_FILE=/app/logs/app.log        # Log file path
LOG_MAX_SIZE=104857600            # 100MB max log file size
LOG_BACKUP_COUNT=10               # Keep 10 rotated log files

# Performance
WORKERS=4                          # Number of worker processes
WORKER_THREADS=2                  # Threads per worker
TIMEOUT=30                         # Request timeout (seconds)

# Monitoring
METRICS_ENABLED=true               # Enable metrics collection
SENTRY_DSN=                        # Sentry error tracking (optional)
```

### Configuration File (.env)

```env
# Application
PORT=2317
FLASK_ENV=production
LOG_LEVEL=info

# Database
DATABASE_PATH=/var/geneweb/bases

# Backend
BACKEND=ocaml

# Logging
LOG_FILE=/var/log/geneweb/app.log
```

## Health Checks

### Application Health Endpoint

```bash
# Check application health
curl http://localhost:2317/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-10-31T10:00:00Z"}
```

### Readiness Check

```bash
# Check if application is ready
curl http://localhost:2317/ready

# Expected response when ready:
# {"status": "ready"}
```

### Liveness Check

```bash
# Check if application is alive
curl http://localhost:2317/alive

# Expected response:
# {"status": "alive"}
```

## Monitoring & Logs

### View Application Logs

```bash
# Local logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f geneweb

# Systemd logs
sudo journalctl -u geneweb -f

# Filter by level
tail -f logs/app.log | grep ERROR
```

### Log Rotation

Logs are automatically rotated when reaching max size.

Configuration in `python_app/app.py`:
```python
handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=104857600,  # 100MB
    backupCount=10
)
```

### Monitoring Metrics

Access metrics endpoint (if enabled):

```bash
curl http://localhost:2317/metrics
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port
lsof -i :2317

# Kill process
kill -9 <PID>

# Or use pkill
pkill -f "python.*app.py"
```

#### Database Not Found

```bash
# Check database path
ls -la /path/to/bases/

# Verify DATABASE_PATH environment variable
echo $DATABASE_PATH

# Create bases directory if missing
mkdir -p /app/bases
```

#### OCaml Backend Not Running

```bash
# Check if gwd is running
ps aux | grep gwd

# Start gwd
cd GeneWeb
./gw/gwd -hd ./gw -bd ./bases -p 23179 -lang en &
cd ..
```

#### Connection Refused

```bash
# Check application is running
curl http://localhost:2317/health

# Check logs for errors
tail -f logs/app.log

# Verify port configuration
echo $PORT
```

#### Docker Container Exits Immediately

```bash
# Check logs
docker-compose logs geneweb

# Check health status
docker ps

# Rebuild image
docker-compose up -d --build
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export LOG_LEVEL=debug
export FLASK_DEBUG=1

# Run application
python -m python_app.app
```

### Performance Issues

Check system resources:

```bash
# CPU and memory usage
top

# Disk space
df -h

# Network connections
netstat -an | grep 2317

# Application metrics
curl http://localhost:2317/metrics
```

## Backup & Recovery

### Backup Database

```bash
# Backup GWB database
cp -r GeneWeb/bases GeneWeb/bases.backup.$(date +%Y%m%d)

# Compress backup
tar -czf geneweb-backup-$(date +%Y%m%d).tar.gz GeneWeb/bases
```

### Backup Logs

```bash
# Backup application logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### Restore from Backup

```bash
# Restore database
cp -r GeneWeb/bases.backup.YYYYMMDD GeneWeb/bases

# Restart application
docker-compose restart geneweb
```

## Performance Tuning

### Python Application Tuning

```python
# In python_app/app.py
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
```

### System Tuning

```bash
# Increase file descriptors
ulimit -n 65536

# Tune network settings
sudo sysctl -w net.core.somaxconn=65536
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=65536
```

## Security Best Practices

### 1. Use HTTPS

Always use HTTPS in production (See SSL/HTTPS Setup above).

### 2. Environment Variables

Never commit secrets to git. Use `.env` file with:
```bash
echo ".env" >> .gitignore
```

### 3. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 4. Access Control

```bash
# Restrict file permissions
chmod 600 .env
chmod 700 logs/

# Set correct ownership
chown geneweb:geneweb /var/geneweb/bases
```

### 5. Regular Updates

```bash
# Update Python dependencies
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Update system packages
sudo apt-get update && sudo apt-get upgrade
```

## Support

For issues or questions:

- Check [Troubleshooting](#troubleshooting) section
- Review [README.md](../README.md)
- Check [GitHub Issues](https://github.com/Antonyjin/Legacy-Project/issues)
- Review logs for error messages

---

**Last Updated**: October 31, 2025  
**Version**: 1.0.0
