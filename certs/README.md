# SSL Certificates Directory

Place your SSL certificates here for HTTPS support.

## Required Files

When `SSL_ENABLED=true` in your `.env` file:

1. **`server_certificate.pem`** - Your SSL certificate (or certificate chain)
2. **`server_key.key`** - Your private key (unencrypted)

## Generating Self-Signed Certificates (Development Only)

```bash
# Generate a self-signed certificate valid for 365 days
openssl req -x509 -newkey rsa:4096 -keyout server_key.key -out server_certificate.pem -days 365 -nodes -subj "/CN=localhost"
```

## Using Let's Encrypt (Production)

For production, use Let's Encrypt with certbot:

```bash
# Install certbot
sudo apt install certbot

# Generate certificate (standalone mode)
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to this directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./server_certificate.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./server_key.key
sudo chmod 644 server_certificate.pem server_key.key
```

## Configuration

In your `.env` file:

```env
SSL_ENABLED=true
SSL_CERT_DIR=/opt/license_tracker/certs
SSL_CERT_FILE=server_certificate.pem
SSL_KEY_FILE=server_key.key
```

## Security Notes

- **NEVER** commit certificates or private keys to version control
- Keep private keys secure with restricted permissions (`chmod 600`)
- Renew certificates before expiration
- Consider using a reverse proxy (nginx/traefik) for SSL termination in production
