#!/usr/bin/env python
"""
Generate expanded dummy data for license_tracker database.
This script generates license_history_logs data by multiplying the base data by 100x.
"""

import random
from datetime import datetime, timedelta

# Base configuration - same apps and features
APPS_CONFIG = {
    'MSC': {
        'server': 'license-server-{region}',
        'software_features': [
            ('MSC Nastran', 'nastran', '2024.1'),
            ('MSC Patran', 'patran', '2024.1'),
            ('MSC Marc', 'marc', '2024.1'),
        ],
        'total_licenses': {'nastran': 100, 'patran': 50, 'marc': 40}
    },
    'Altair': {
        'server': 'license-server-{region}',
        'software_features': [
            ('Altair HyperWorks', 'hyperworks', '2024.0'),
            ('Altair HyperMesh', 'hypermesh', '2024.0'),
            ('Altair Radioss', 'radioss', '2024.0'),
        ],
        'total_licenses': {'hyperworks': 75, 'hypermesh': 75, 'radioss': 60}
    },
    'RLM': {
        'server': 'license-server-{region}',
        'software_features': [
            ('MASTA', 'masta', '12.0'),
        ],
        'total_licenses': {'masta': 25}
    },
    'Particleworks': {
        'server': 'license-server-{region}',
        'software_features': [
            ('Particleworks', 'particleworks', '8.0'),
        ],
        'total_licenses': {'particleworks': 10}
    }
}

REGIONS = ['EU', 'APAC', 'AME']
REGION_SERVERS = {'EU': 'eu', 'APAC': 'apac', 'AME': 'ame'}

USERS = [
    ('john.doe', 'workstation-01', 'EU-LON'),
    ('jane.smith', 'workstation-02', 'EU-LON'),
    ('bob.wilson', 'workstation-03', 'APAC-SG'),
    ('alice.chen', 'workstation-04', 'EU-BER'),
    ('admin', 'server-01', 'HQ'),
    ('mike.jones', 'workstation-10', 'US-NYC'),
    ('sarah.lee', 'workstation-11', 'APAC-SG'),
    ('david.kim', 'workstation-12', 'EU-LON'),
    ('emma.white', 'workstation-13', 'US-NYC'),
    ('chris.brown', 'workstation-14', 'EU-BER'),
]

def generate_license_history_logs(num_records=2000):
    """Generate license history log entries."""
    records = []
    base_date = datetime(2026, 1, 31, 12, 0, 0)
    
    for i in range(num_records):
        # Pick random app
        app = random.choice(list(APPS_CONFIG.keys()))
        config = APPS_CONFIG[app]
        
        # Pick random feature
        software, feature, version = random.choice(config['software_features'])
        total_license = config['total_licenses'][feature]
        
        # Pick random region and user
        region = random.choice(REGIONS)
        server = config['server'].format(region=REGION_SERVERS[region])
        
        user, host, site_code = random.choice(USERS)
        user_key = f"{user}@{host}"
        
        # Generate random timestamp going back up to 365 days
        days_ago = random.randint(0, 365)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        date_time = base_date - timedelta(days=days_ago, hours=hours_offset, minutes=minutes_offset)
        
        # Random license usage
        license_used = random.randint(1, 5)
        total_license_used = random.randint(int(total_license * 0.2), int(total_license * 0.9))
        
        records.append({
            'application': app,
            'region': region,
            'user': user,
            'server': server,
            'host': host,
            'software': software,
            'feature': feature,
            'version': version,
            'user_key': user_key,
            'date_time': date_time.strftime('%Y-%m-%d %H:%M:%S'),
            'license_used': license_used,
            'site_code': site_code,
            'total_license': total_license,
            'total_license_used': total_license_used
        })
    
    return records


def generate_sql_file(output_path='init-db/02-dummy-data.sql'):
    """Generate the complete dummy data SQL file."""
    
    # Static parts
    header = """-- Insert dummy data for license_tracker

USE license_tracker;

-- Insert dummy users (password for all test users is 'password', except user_1 which is 'pass')
-- Password hash is bcrypt hash of 'password' or pbkdf2 hash for user_1
INSERT INTO local_users (login, email, password_hash, type, site_code, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'ADMIN', 'HQ', TRUE),
('john.doe', 'john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'EU-LON', TRUE),
('jane.smith', 'jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'US-NYC', TRUE),
('bob.wilson', 'bob.wilson@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'APAC-SG', TRUE),
('alice.chen', 'alice.chen@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'EU-BER', TRUE),
('user_1', 'user_1@example.com', 'pbkdf2:sha256:260000$temp$willberesetbyapp', 'USER', 'HQ', TRUE),
('mike.jones', 'mike.jones@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'US-NYC', TRUE),
('sarah.lee', 'sarah.lee@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'APAC-SG', TRUE),
('david.kim', 'david.kim@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'EU-LON', TRUE),
('emma.white', 'emma.white@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'US-NYC', TRUE),
('chris.brown', 'chris.brown@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'EU-BER', TRUE);

-- Insert default app settings
INSERT INTO app_settings (setting_key, setting_value, setting_type, description) VALUES
('auth_mode', 'local', 'string', 'Authentication mode: local, ldap, or redmine'),
('ldap_enabled', 'false', 'boolean', 'Enable LDAP authentication'),
('ldap_server', '', 'string', 'LDAP server URL (e.g., ldap://ldap.example.com)'),
('ldap_port', '389', 'integer', 'LDAP server port'),
('ldap_use_ssl', 'false', 'boolean', 'Use SSL for LDAP connection'),
('ldap_bind_dn', '', 'string', 'LDAP bind DN (e.g., cn=admin,dc=example,dc=com)'),
('ldap_bind_password', '', 'string', 'LDAP bind password'),
('ldap_base_dn', '', 'string', 'LDAP base DN for user search (e.g., ou=users,dc=example,dc=com)'),
('ldap_user_filter', '(uid={username})', 'string', 'LDAP user search filter'),
('ldap_username_attribute', 'uid', 'string', 'LDAP attribute for username'),
('ldap_email_attribute', 'mail', 'string', 'LDAP attribute for email'),
('registration_enabled', 'true', 'boolean', 'Allow new user registration'),
('redmine_auth_enabled', 'false', 'boolean', 'Enable Redmine/ERM authentication');

-- Insert dummy license details (currently active licenses)
INSERT INTO license_details (application, region, user, host, feature, user_key, license_used, site_code, check_out, check_in, spent_hours, total_license, total_license_used) VALUES
('MSC', 'EU', 'john.doe', 'workstation-01', 'nastran', 'john.doe@workstation-01', 2, 'EU-LON', '2026-01-31 08:00:00', NULL, NULL, 100, 45),
('MSC', 'EU', 'jane.smith', 'workstation-02', 'patran', 'jane.smith@workstation-02', 1, 'EU-LON', '2026-01-31 09:30:00', NULL, NULL, 50, 22),
('MSC', 'APAC', 'bob.wilson', 'workstation-03', 'nastran', 'bob.wilson@workstation-03', 3, 'APAC-SG', '2026-01-31 07:00:00', NULL, NULL, 100, 67),
('Altair', 'EU', 'alice.chen', 'workstation-04', 'hyperworks', 'alice.chen@workstation-04', 1, 'EU-BER', '2026-01-31 10:15:00', NULL, NULL, 75, 34),
('Altair', 'AME', 'john.doe', 'workstation-05', 'hypermesh', 'john.doe@workstation-05', 2, 'US-NYC', '2026-01-31 14:00:00', NULL, NULL, 75, 28),
('MSC', 'AME', 'jane.smith', 'workstation-06', 'marc', 'jane.smith@workstation-06', 1, 'US-NYC', '2026-01-31 13:45:00', NULL, NULL, 40, 18),
('RLM', 'EU', 'bob.wilson', 'workstation-07', 'masta', 'bob.wilson@workstation-07', 1, 'EU-LON', '2026-01-31 11:00:00', NULL, NULL, 25, 12),
('Altair', 'APAC', 'alice.chen', 'workstation-08', 'radioss', 'alice.chen@workstation-08', 2, 'APAC-SG', '2026-01-31 06:30:00', NULL, NULL, 60, 41),
('MSC', 'EU', 'admin', 'server-01', 'nastran', 'admin@server-01', 5, 'HQ', '2026-01-31 05:00:00', NULL, NULL, 100, 45),
('Particleworks', 'APAC', 'bob.wilson', 'workstation-09', 'particleworks', 'bob.wilson@workstation-09', 1, 'APAC-SG', '2026-01-31 08:30:00', NULL, NULL, 10, 6);

-- Insert dummy license history logs (expanded - 2000 records spanning 365 days)
INSERT INTO license_history_logs (application, region, user, server, host, software, feature, version, user_key, date_time, license_used, site_code, total_license, total_license_used) VALUES
"""
    
    # Generate records
    records = generate_license_history_logs(2000)
    
    # Format as SQL values
    values = []
    for r in records:
        value = f"('{r['application']}', '{r['region']}', '{r['user']}', '{r['server']}', '{r['host']}', '{r['software']}', '{r['feature']}', '{r['version']}', '{r['user_key']}', '{r['date_time']}', {r['license_used']}, '{r['site_code']}', {r['total_license']}, {r['total_license_used']})"
        values.append(value)
    
    # Join with commas and newlines
    sql_content = header + ',\n'.join(values) + ';\n'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"Generated {len(records)} license history records to {output_path}")


if __name__ == '__main__':
    import os
    import sys
    
    # Determine output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_path = os.path.join(project_root, 'init-db', '02-dummy-data.sql')
    
    # Allow override via command line
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    
    generate_sql_file(output_path)
