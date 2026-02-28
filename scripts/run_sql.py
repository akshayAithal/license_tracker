#!/usr/bin/env python
"""
Standalone script to execute SQL files against the license_tracker database.

Usage:
    python run_sql.py <sql_file> [--host HOST] [--port PORT] [--user USER] [--password PASSWORD] [--database DATABASE]
    
Examples:
    # Using environment variables from .env
    python run_sql.py init-db/02-dummy-data.sql
    
    # With explicit connection parameters
    python run_sql.py update.sql --host localhost --port 3306 --user license_user --password license_password
    
    # Run against Docker container
    python run_sql.py init-db/02-dummy-data.sql --host 127.0.0.1 --port 3306
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import pymysql
except ImportError:
    print("Error: pymysql is required. Install it with: pip install pymysql")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_env_config():
    """Load configuration from .env file if available."""
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'license_user',
        'password': 'license_password',
        'database': 'license_tracker'
    }
    
    # Try to load .env file
    if load_dotenv:
        env_paths = [
            Path(__file__).parent.parent / '.env',
            Path(__file__).parent.parent / 'instance' / '.env',
            Path.cwd() / '.env'
        ]
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break
    
    # Override with environment variables
    config['host'] = os.getenv('MYSQL_HOST', os.getenv('DB_HOST', 'localhost'))
    config['port'] = int(os.getenv('MYSQL_PORT', os.getenv('DB_PORT', 3306)))
    config['user'] = os.getenv('MYSQL_USER', 'license_user')
    config['password'] = os.getenv('MYSQL_PASSWORD', 'license_password')
    config['database'] = os.getenv('MYSQL_DATABASE', 'license_tracker')
    
    # Parse from SQLALCHEMY_DATABASE_URI if available
    uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if uri and 'mysql' in uri:
        try:
            # mysql+pymysql://user:password@host:port/database
            from urllib.parse import urlparse
            parsed = urlparse(uri.replace('mysql+pymysql://', 'mysql://'))
            if parsed.hostname:
                config['host'] = parsed.hostname
            if parsed.port:
                config['port'] = parsed.port
            if parsed.username:
                config['user'] = parsed.username
            if parsed.password:
                config['password'] = parsed.password
            if parsed.path:
                config['database'] = parsed.path.lstrip('/')
        except Exception:
            pass
    
    return config


def execute_sql_file(sql_file: str, host: str, port: int, user: str, password: str, database: str, verbose: bool = True):
    """Execute a SQL file against the database."""
    
    sql_path = Path(sql_file)
    if not sql_path.exists():
        print(f"Error: SQL file not found: {sql_file}")
        return False
    
    if verbose:
        print(f"Reading SQL file: {sql_path.absolute()}")
    
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    if verbose:
        print(f"Connecting to MySQL: {user}@{host}:{port}/{database}")
    
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f"Error connecting to database: {e}")
        return False
    
    try:
        with connection.cursor() as cursor:
            # Split SQL content by semicolons, handling multi-statement execution
            # Filter out empty statements and comments-only statements
            statements = []
            current_statement = []
            
            for line in sql_content.split('\n'):
                stripped = line.strip()
                
                # Skip empty lines and comment-only lines for statement building
                if not stripped or stripped.startswith('--'):
                    continue
                
                current_statement.append(line)
                
                # Check if line ends with semicolon (end of statement)
                if stripped.endswith(';'):
                    statement = '\n'.join(current_statement).strip()
                    if statement and not statement.startswith('--'):
                        statements.append(statement)
                    current_statement = []
            
            # Handle any remaining statement without semicolon
            if current_statement:
                statement = '\n'.join(current_statement).strip()
                if statement and not statement.startswith('--'):
                    statements.append(statement)
            
            if verbose:
                print(f"Executing {len(statements)} SQL statement(s)...")
            
            for i, statement in enumerate(statements, 1):
                try:
                    # Skip USE statements if we're already connected to the right database
                    if statement.upper().startswith('USE '):
                        if verbose:
                            print(f"  [{i}/{len(statements)}] Skipping USE statement (already connected)")
                        continue
                    
                    cursor.execute(statement)
                    affected = cursor.rowcount
                    if verbose:
                        # Show first 50 chars of statement
                        preview = statement[:50].replace('\n', ' ')
                        if len(statement) > 50:
                            preview += '...'
                        print(f"  [{i}/{len(statements)}] {preview} ({affected} rows affected)")
                except pymysql.Error as e:
                    print(f"Error executing statement {i}: {e}")
                    print(f"Statement: {statement[:200]}...")
                    return False
        
        if verbose:
            print("SQL file executed successfully!")
        return True
        
    except pymysql.Error as e:
        print(f"Error executing SQL: {e}")
        return False
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(
        description='Execute SQL files against the license_tracker MySQL database.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_sql.py init-db/02-dummy-data.sql
    python run_sql.py update.sql --host localhost --port 3306
    python run_sql.py --clear-history  # Clear all license history logs
        """
    )
    
    parser.add_argument('sql_file', nargs='?', help='Path to SQL file to execute')
    parser.add_argument('--host', help='MySQL host (default: from .env or localhost)')
    parser.add_argument('--port', type=int, help='MySQL port (default: from .env or 3306)')
    parser.add_argument('--user', '-u', help='MySQL user (default: from .env or license_user)')
    parser.add_argument('--password', '-p', help='MySQL password (default: from .env)')
    parser.add_argument('--database', '-d', help='MySQL database (default: from .env or license_tracker)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress verbose output')
    parser.add_argument('--clear-history', action='store_true', help='Clear all license_history_logs before running SQL')
    
    args = parser.parse_args()
    
    # Load defaults from environment
    config = load_env_config()
    
    # Override with command line arguments
    if args.host:
        config['host'] = args.host
    if args.port:
        config['port'] = args.port
    if args.user:
        config['user'] = args.user
    if args.password:
        config['password'] = args.password
    if args.database:
        config['database'] = args.database
    
    verbose = not args.quiet
    
    # Handle --clear-history option
    if args.clear_history:
        if verbose:
            print("Clearing license_history_logs table...")
        
        try:
            connection = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                charset='utf8mb4',
                autocommit=True
            )
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM license_history_logs")
                print(f"Cleared {cursor.rowcount} rows from license_history_logs")
            connection.close()
        except pymysql.Error as e:
            print(f"Error clearing history: {e}")
            return 1
    
    # Execute SQL file if provided
    if args.sql_file:
        success = execute_sql_file(
            args.sql_file,
            config['host'],
            config['port'],
            config['user'],
            config['password'],
            config['database'],
            verbose
        )
        return 0 if success else 1
    elif not args.clear_history:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
