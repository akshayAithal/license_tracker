#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for product_viewer."""
from license_tracker.logger import logger
from license_tracker.app import create_app


#if __name__ == "__main__":
logger.warning(
    "Run this using a WSGI server. "
    "Running via Flask's "
    "run command is not recommended.")
app = create_app(config_filename="config.py")
app.run(host="0.0.0.0",port="2323",threaded=True)
#,ssl_context=(r'C:\Users\akshay.aithal\Documents\certs\localhost\server_certificate.pem',r'C:\Users\akshay.aithal\Documents\certs\localhost\server_key.key'))
