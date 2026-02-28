# License Tracker - Deployment Guide

## Quick Start

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration (passwords, secrets, license servers)

3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

---

## Environment Configuration

All configuration is now centralized in the `.env` file. The application reads from:

1. **Docker Compose**: Uses `env_file: .env` to load all variables
2. **Python (config.py)**: Uses `python-dotenv` to load `.env` from instance folder
3. **Gunicorn**: Loads `.env` before starting the Flask app

### Local Development (HTTP)

```env
SSL_ENABLED=false
BACKEND_URL=http://localhost:2324
CORS_ORIGINS=http://localhost:3000
```

### Production (HTTPS)

```env
SSL_ENABLED=true
SSL_CERT_DIR=/opt/license_tracker/certs
SSL_CERT_FILE=server_certificate.pem
SSL_KEY_FILE=server_key.key
BACKEND_URL=https://yourdomain.com:2324
CORS_ORIGINS=https://yourdomain.com
```

---

## SSL/HTTPS Setup

### Where to Add Certificates

1. Create a `certs/` folder in your project root
2. Place your certificates:
   - `certs/server_certificate.pem` - SSL certificate
   - `certs/server_key.key` - Private key

3. The certificates are mounted into the container via docker-compose

### Generate Self-Signed Certificate (Development)

```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout certs/server_key.key \
  -out certs/server_certificate.pem \
  -days 365 -nodes \
  -subj "/CN=localhost"
```

### Let's Encrypt (Production)

```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy to project
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem certs/server_certificate.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem certs/server_key.key
```

---

## Server Deployment Options

### Option 1: Docker Compose (Recommended)

You're already using this. Additional recommendations:

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up -d --build

# Stop
docker-compose down
```

### Option 2: Docker Compose with Reverse Proxy (Traefik)

Add Traefik for automatic SSL and better routing:

```yaml
# docker-compose.override.yml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    networks:
      - frontend-network

  backend:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
```

### Option 3: Systemd Service (Without Docker)

For running directly on Linux:

```ini
# /etc/systemd/system/license-tracker.service
[Unit]
Description=License Tracker Backend
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/license_tracker
EnvironmentFile=/opt/license_tracker/.env
ExecStart=/usr/bin/python3 deploy_gunicorn.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Alternatives to .env File

### 1. Docker Secrets (Docker Swarm)

For Docker Swarm deployments:

```yaml
# docker-compose.yml
secrets:
  db_password:
    external: true
  secret_key:
    external: true

services:
  backend:
    secrets:
      - db_password
      - secret_key
```

### 2. HashiCorp Vault

For enterprise secrets management:

```python
# In config.py
import hvac
client = hvac.Client(url='http://vault:8200')
SECRET_KEY = client.secrets.kv.read_secret_version(path='license-tracker')['data']['data']['secret_key']
```

### 3. Environment Variables via Cloud Provider

- **AWS**: Systems Manager Parameter Store, Secrets Manager
- **Azure**: Key Vault
- **GCP**: Secret Manager

### 4. Kubernetes Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: license-tracker-secrets
type: Opaque
stringData:
  SECRET_KEY: "your-secret-key"
  MYSQL_PASSWORD: "your-db-password"
```

---

## GitHub CI/CD - Auto Deploy to Server

### Option 1: GitHub Actions with SSH

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Server

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/license_tracker
            git pull origin main
            docker-compose down
            docker-compose up -d --build
```

**Required GitHub Secrets:**
- `SERVER_HOST` - Your server IP/hostname
- `SERVER_USER` - SSH username
- `SSH_PRIVATE_KEY` - Private key for SSH access

### Option 2: GitHub Actions with Docker Hub

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: yourusername/license-tracker:latest
          file: backend/Dockerfile

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            docker pull yourusername/license-tracker:latest
            cd /opt/license_tracker
            docker-compose up -d
```

### Option 3: Watchtower (Auto-update containers)

Run Watchtower on your server to automatically pull and restart containers:

```yaml
# Add to docker-compose.yml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_POLL_INTERVAL=300
      - WATCHTOWER_CLEANUP=true
```

### Option 4: Webhook + Git Pull

1. Install webhook server on your machine
2. Configure GitHub webhook to trigger on push
3. Script pulls and rebuilds on trigger

```bash
# /opt/scripts/deploy.sh
#!/bin/bash
cd /opt/license_tracker
git pull origin main
docker-compose up -d --build
```

---

## Server Setup Checklist

- [ ] Copy `.env.example` to `.env` on server
- [ ] Configure all sensitive values in `.env`
- [ ] Create `certs/` directory with SSL certificates (if using HTTPS)
- [ ] Set `SSL_ENABLED=true` for production
- [ ] Configure firewall (ports 2324, 3000, 3306)
- [ ] Set up automatic backups for MySQL data
- [ ] Configure log rotation
- [ ] Set up monitoring (optional: Prometheus, Grafana)

---

## Security Recommendations

1. **Never commit `.env`** - It's already in `.gitignore`
2. **Use strong passwords** - Generate with `openssl rand -hex 32`
3. **Rotate secrets regularly**
4. **Use a reverse proxy** (nginx/traefik) for SSL termination
5. **Keep Docker images updated**
6. **Restrict database access** to internal network only
