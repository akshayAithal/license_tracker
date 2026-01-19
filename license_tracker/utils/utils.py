

    
def construct_uri(ip, port, db_type, db, username, password):
    """Returns an uri for SQLAlchemy using the given parameters."""
    try:
        from urllib import quote_plus
    except ImportError:
        from urllib.parse import quote_plus

    db_type = db_type.lower()
    if db_type == "mysql":
        dialect_driver = "mysql+pymysql"
    elif db_type == "postgresql":
        dialect_driver = "postgres+psycopg2"
    else:
        raise NotImplementedError(("Unable to process {} "
                                   "databases for now.").format(db_type))
    
    uri = "{}://{}:{}@{}:{}/{}".format(dialect_driver, username,
                                       quote_plus(password), ip,
                                       port, db)
    return uri