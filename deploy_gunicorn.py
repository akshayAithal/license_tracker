import os
from pathlib import Path
from dotenv import load_dotenv
import gunicorn.app.base

# Load .env file - check instance folder first, then project root
instance_env = Path(__file__).parent / 'instance' / '.env'
root_env = Path(__file__).parent / '.env'

if instance_env.exists():
    load_dotenv(instance_env)
elif root_env.exists():
    load_dotenv(root_env)

from license_tracker.app import create_app


def number_of_workers():
    return int(os.getenv("GUNICORN_WORKERS", "10"))


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def is_ssl_enabled():
    """Check if SSL is enabled via environment variable."""
    ssl_enabled = os.getenv("SSL_ENABLED", "false").lower()
    return ssl_enabled in ("true", "1", "yes")


def get_ssl_paths():
    """Get SSL certificate and key paths from environment."""
    cert_dir = os.getenv("SSL_CERT_DIR", "/opt/license_tracker/certs")
    cert_file = os.getenv("SSL_CERT_FILE", "server_certificate.pem")
    key_file = os.getenv("SSL_KEY_FILE", "server_key.key")
    
    cert_path = os.path.join(cert_dir, cert_file)
    key_path = os.path.join(cert_dir, key_file)
    
    return cert_path, key_path


if __name__ == '__main__':
    app = create_app(config_filename="config.py")
    
    # Get configuration from environment
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = os.getenv("BACKEND_PORT", "2324")
    timeout = int(os.getenv("GUNICORN_TIMEOUT", "240"))
    log_level = os.getenv("GUNICORN_LOG_LEVEL", "debug")
    
    # Base options
    options = {
        'bind': f'{host}:{port}',
        'workers': number_of_workers(),
        'timeout': timeout,
        'log-level': log_level,
    }
    
    # Add SSL options if enabled
    if is_ssl_enabled():
        cert_path, key_path = get_ssl_paths()
        
        # Verify certificates exist
        if not os.path.exists(cert_path):
            print(f"WARNING: SSL certificate not found at {cert_path}")
        if not os.path.exists(key_path):
            print(f"WARNING: SSL key not found at {key_path}")
        
        options['certfile'] = cert_path
        options['keyfile'] = key_path
        options['limit_request_line'] = 0
        print(f"Starting server with HTTPS on {host}:{port}")
    else:
        print(f"Starting server with HTTP on {host}:{port}")
    
    StandaloneApplication(app, options).run()