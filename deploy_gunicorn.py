import multiprocessing

import gunicorn.app.base


def number_of_workers():
    return 10 #(multiprocessing.cpu_count() * 2) + 1

from license_tracker.app import create_app

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



if __name__ == '__main__':
    app = create_app(config_filename="config.py")
    import os
    if os.getenv("SSL_CERT_DIR"):
        cert_path = os.getenv("SSL_CERT_DIR") 
        cert_full_path = os.path.join(cert_path,"server_certificate.pem")
        key_full_path = os.path.join(cert_path,"server_key.key")
    else:
        cert_full_path ='/cert/server_certificate.pem'
        key_full_path = '/cert/server_key.key'
    if os.getenv("SSL_ENABLED"):
        options = {
        'bind': '%s:%s' % ('0.0.0.0', '2324'),
        'workers': number_of_workers(),
        'timeout': 240,
        'log-level': 'debug',
        'certfile':cert_full_path,
        'keyfile':key_full_path,
        'limit_request_line':0
    }
    else:
        options ={
        'bind': '%s:%s' % ('0.0.0.0', '2324'),
        'workers': number_of_workers(),
        'timeout': 240,
        'log-level': 'debug',
    }
    StandaloneApplication(app, options).run()