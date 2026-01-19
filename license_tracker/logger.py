#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.handlers

import coloredlogs

# TODO:
# Push this to a separate library that can take a logger name and
# return a logger.

logger = logging.getLogger("license_tracker")
logger.setLevel(logging.DEBUG)
# coloredlogs.install(level="DEBUG")
coloredlogs.install(level="DEBUG", logger=logger)
# create formatter


# create console handler and set level to debug

# ch = logging.StreamHandler()
# ch.setLevel(logging.WARNING)
# ch.setFormatter(formatter)
# logger.addHandler(ch)


fh_fmt = (
    "%(asctime)s - [%(levelname)s] [%(name)s] "
    "[%(filename)s:%(lineno)s - %(funcName)s()] "
    "%(message)s")
fh_formatter = logging.Formatter(fh_fmt)
fh = logging.handlers.RotatingFileHandler(
    'license_tracker.log', maxBytes=1024*1024, backupCount=10)
fh.setLevel(logging.DEBUG)
fh.setFormatter(fh_formatter)
logger.addHandler(fh)

# add ch to logger
logger.debug("Created logger.")


def install_logger(application,logger_name = "default_logger"):
    """Installs logger on flask and werkzeug objects."""
    import logging
    import logging.handlers
    import coloredlogs
    logging.getLogger(logger_name).setLevel(logging.DEBUG)
    logging.getLogger(logger_name).addHandler(fh)
    application.logger.setLevel(logging.DEBUG)
    request_fh_fmt = (
        "%(asctime)s - [%(levelname)s] [%(name)s] "
        "[%(filename)s:%(lineno)s - %(funcName)s()] "
        "%(message)s")
    request_fh_formatter = logging.Formatter(request_fh_fmt)
    request_fh = logging.handlers.RotatingFileHandler(
        '{}_requests.log'.format(logger_name), maxBytes=1024*1024, backupCount=10)
    request_fh.setLevel(logging.DEBUG)
    request_fh.setFormatter(request_fh_formatter)
    application.logger.addHandler(request_fh)
    coloredlogs.install(level="DEBUG", logger=application.logger)
    coloredlogs.install(level="DEBUG", logger=logging.getLogger(logger_name))
