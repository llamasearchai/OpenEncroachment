# OpenEncroachment Deployment Guide

This guide covers various deployment options for the OpenEncroachment system.

## Prerequisites

- Python 3.10+
- OpenAI API key
- Docker (optional but recommended)
- uv package manager (recommended)

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/open-encroachment.git
cd open-encroachment
```

### 2. Configure Environment Variables
```bash
# Copy environment template
cp env.template .env

# Edit .env file with your values
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_AGENT_MODEL=gpt-4o-mini
HOST=0.0.0.0
PORT=8000
```

## Deployment Options

### Option 1: Local Development

#### Using uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync environment
~/.local/bin/uv sync --all-extras --dev

# Run API server
~/.local/bin/uv run uvicorn open_encroachment.api:app --reload --host 0.0.0.0 --port 8000
```

#### Using pip
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e .[dev]

# Run API server
uvicorn open_encroachment.api:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Docker Deployment

#### Using Docker Compose (Recommended)
```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Using Docker Directly
```bash
# Build image
docker build -t open-encroachment .

# Run container
docker run -d \
  --name open-encroachment \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e OPENAI_AGENT_MODEL=gpt-4o-mini \
  -v $(pwd)/artifacts:/app/artifacts \
  -v $(pwd)/outbox:/app/outbox \
  -v $(pwd)/logs:/app/logs \
  open-encroachment
```

### Option 3: Production Deployment

#### Systemd Service
Create `/etc/systemd/system/open-encroachment.service`:
```ini
[Unit]
Description=OpenEncroachment API Server
After=network.target

[Service]
Type=simple
User=opencroach
Group=opencroach
WorkingDirectory=/opt/open-encroachment
Environment=PATH=/opt/open-encroachment/.venv/bin
Environment=OPENAI_API_KEY=your_key_here
ExecStart=/opt/open-encroachment/.venv/bin/uvicorn open_encroachment.api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable open-encroachment
sudo systemctl start open-encroachment
sudo systemctl status open-encroachment
```

#### Nginx Reverse Proxy
Create `/etc/nginx/sites-available/open-encroachment`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/open-encroachment /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### SSL with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Certificates will auto-renew
```

## Configuration

### Application Configuration
Edit `config/settings.yaml`:
```yaml
geofences:
  - id: your_geofence
    name: Your Protected Area
    polygon:
      - [lat1, lon1]
      - [lat2, lon2]
      - [lat3, lon3]
      - [lat4, lon4]

dispatch:
  mode: webhook  # or 'local'
  outbox_dir: outbox
  webhook:
    url: https://your-webhook-endpoint.com/notify
    timeout: 10.0
    headers:
      X-API-Key: your-webhook-key

thresholds:
  severity_notify_min: 0.6
  severity_escalate_min: 0.8

artifacts:
  models_dir: artifacts/models
  predictions_dir: artifacts/predictions
  db_path: artifacts/case_manager.db
  evidence_ledger: artifacts/evidence_ledger.jsonl
```

### Dispatcher Configuration
Create `config/dispatcher.yaml` for webhook configuration:
```yaml
mode: webhook
webhook:
  url: https://api.example.com/webhooks/encroachment
  timeout: 10.0
  ca_bundle: /path/to/ca.pem
  client_cert: /path/to/cert.pem
  client_key: /path/to/key.pem
  headers:
    Authorization: Bearer your-token
    Content-Type: application/json
```

## Data Setup

### Create Required Directories
```bash
mkdir -p artifacts/models
mkdir -p artifacts/predictions
mkdir -p outbox
mkdir -p logs
mkdir -p data/satellite
mkdir -p data/aerial
mkdir -p data/ground
mkdir -p data/gps
mkdir -p data/social
```

### Initialize Database
```bash
# Run pipeline once to initialize database
open-encroachment run-pipeline --config config/settings.yaml --sample-data
```

## Monitoring and Logging

### Application Logs
```bash
# View application logs
docker-compose logs -f open-encroachment

# Or for systemd
sudo journalctl -u open-encroachment -f
```

### Health Checks
```bash
# API health check
curl http://localhost:8000/health

# Pipeline test
curl -X POST http://localhost:8000/api/v1/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"use_sample_data": true}'
```

### Monitoring Setup
Consider setting up monitoring with:
- Prometheus for metrics collection
- Grafana for dashboards
- ELK stack for log aggregation
- AlertManager for notifications

## Backup and Recovery

### Database Backup
```bash
# SQLite database backup
cp artifacts/case_manager.db artifacts/case_manager.db.backup

# Automated backup script
#!/bin/bash
BACKUP_DIR="/opt/backups/open-encroachment"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp artifacts/case_manager.db $BACKUP_DIR/case_manager_$DATE.db
find $BACKUP_DIR -name "case_manager_*.db" -mtime +30 -delete
```

### Configuration Backup
```bash
# Backup configuration files
tar -czf config_backup.tar.gz config/
```

### Model Backup
```bash
# Backup trained models
tar -czf models_backup.tar.gz artifacts/models/
```

## Scaling Considerations

### Horizontal Scaling
```bash
# Run multiple instances behind a load balancer
docker-compose up --scale open-encroachment=3

# Use Nginx as load balancer
upstream open_encroachment_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

### Database Scaling
For high-traffic deployments, consider:
- PostgreSQL instead of SQLite
- Redis for caching
- Database connection pooling
- Read replicas for analytics

### Performance Optimization
```bash
# Gunicorn for production serving
pip install gunicorn
gunicorn open_encroachment.api:app -w 4 -k uvicorn.workers.UvicornWorker

# Environment variables for performance
export UVICORN_WORKERS=4
export UVICORN_HOST=0.0.0.0
export UVICORN_PORT=8000
```

## Security Considerations

### Network Security
```bash
# Firewall configuration
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Docker network isolation
docker network create --driver bridge open-encroachment-net
```

### API Security
```python
# Add authentication middleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Implement token verification
    pass
```

### Data Encryption
```bash
# Encrypt sensitive files
openssl enc -aes-256-cbc -salt -in secrets.txt -out secrets.enc

# Environment variable encryption
# Use tools like sops or chamber for secret management
```

## Troubleshooting

### Common Issues

#### API Not Starting
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Check port availability
netstat -tlnp | grep 8000

# Check logs
docker-compose logs open-encroachment
```

#### Database Connection Issues
```bash
# Check database file permissions
ls -la artifacts/case_manager.db

# Reinitialize database
rm artifacts/case_manager.db
open-encroachment run-pipeline --config config/settings.yaml --sample-data
```

#### Memory Issues
```bash
# Monitor memory usage
docker stats

# Adjust Docker memory limits
docker run --memory=2g --memory-swap=4g open-encroachment

# Check for memory leaks in application
```

### Log Analysis
```bash
# Search for errors
grep "ERROR" logs/application.log

# Monitor API response times
grep "POST /api" logs/application.log | grep -o "[0-9]\+\.[0-9]\+s" | sort -n
```

## Maintenance

### Regular Tasks
```bash
# Update dependencies monthly
uv lock --upgrade

# Rotate logs weekly
logrotate /etc/logrotate.d/open-encroachment

# Database maintenance
sqlite3 artifacts/case_manager.db "VACUUM;"

# Security updates
apt update && apt upgrade
```

### Monitoring Commands
```bash
# Check system resources
top -p $(pgrep -f open-encroachment)

# Monitor API endpoints
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Check database size
ls -lh artifacts/case_manager.db
```

This deployment guide covers the essential aspects of setting up OpenEncroachment in various environments. Adjust configurations based on your specific requirements and infrastructure.
