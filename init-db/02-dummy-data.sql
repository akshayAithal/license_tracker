-- Insert dummy data for license_tracker

USE license_tracker;

-- Insert dummy users (password for all test users is 'password', except user_1 which is 'pass')
-- Password hash is bcrypt hash of 'password' or pbkdf2 hash for user_1
INSERT INTO local_users (login, email, password_hash, type, site_code, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'ADMIN', 'HQ', TRUE),
('john.doe', 'john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'EU-LON', TRUE),
('jane.smith', 'jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'US-NYC', TRUE),
('bob.wilson', 'bob.wilson@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'APAC-SG', TRUE),
('alice.chen', 'alice.chen@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.y.0yCwRQ3Y7K', 'USER', 'EU-BER', TRUE),
('user_1', 'user_1@example.com', 'pbkdf2:sha256:260000$temp$willberesetbyapp', 'USER', 'HQ', TRUE);

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

-- Insert dummy license history logs (past usage)
INSERT INTO license_history_logs (application, region, user, server, host, software, feature, version, user_key, date_time, license_used, site_code, total_license, total_license_used) VALUES
('MSC', 'EU', 'john.doe', 'license-server-eu', 'workstation-01', 'MSC Nastran', 'nastran', '2024.1', 'john.doe@workstation-01', '2026-01-30 08:00:00', 2, 'EU-LON', 100, 52),
('MSC', 'EU', 'john.doe', 'license-server-eu', 'workstation-01', 'MSC Nastran', 'nastran', '2024.1', 'john.doe@workstation-01', '2026-01-29 09:00:00', 2, 'EU-LON', 100, 48),
('MSC', 'EU', 'jane.smith', 'license-server-eu', 'workstation-02', 'MSC Patran', 'patran', '2024.1', 'jane.smith@workstation-02', '2026-01-30 10:00:00', 1, 'EU-LON', 50, 25),
('MSC', 'APAC', 'bob.wilson', 'license-server-apac', 'workstation-03', 'MSC Nastran', 'nastran', '2024.1', 'bob.wilson@workstation-03', '2026-01-30 07:30:00', 3, 'APAC-SG', 100, 71),
('MSC', 'APAC', 'bob.wilson', 'license-server-apac', 'workstation-03', 'MSC Nastran', 'nastran', '2024.1', 'bob.wilson@workstation-03', '2026-01-29 06:00:00', 4, 'APAC-SG', 100, 65),
('Altair', 'EU', 'alice.chen', 'license-server-eu', 'workstation-04', 'Altair HyperWorks', 'hyperworks', '2024.0', 'alice.chen@workstation-04', '2026-01-30 11:00:00', 1, 'EU-BER', 75, 38),
('Altair', 'AME', 'john.doe', 'license-server-ame', 'workstation-05', 'Altair HyperMesh', 'hypermesh', '2024.0', 'john.doe@workstation-05', '2026-01-30 14:30:00', 2, 'US-NYC', 75, 31),
('Altair', 'AME', 'jane.smith', 'license-server-ame', 'workstation-06', 'Altair HyperMesh', 'hypermesh', '2024.0', 'jane.smith@workstation-06', '2026-01-29 15:00:00', 1, 'US-NYC', 75, 29),
('MSC', 'AME', 'jane.smith', 'license-server-ame', 'workstation-06', 'MSC Marc', 'marc', '2024.1', 'jane.smith@workstation-06', '2026-01-30 13:00:00', 1, 'US-NYC', 40, 20),
('RLM', 'EU', 'bob.wilson', 'license-server-eu', 'workstation-07', 'MASTA', 'masta', '12.0', 'bob.wilson@workstation-07', '2026-01-30 10:30:00', 1, 'EU-LON', 25, 15),
('RLM', 'EU', 'alice.chen', 'license-server-eu', 'workstation-07', 'MASTA', 'masta', '12.0', 'alice.chen@workstation-07', '2026-01-29 09:30:00', 1, 'EU-LON', 25, 13),
('Altair', 'APAC', 'alice.chen', 'license-server-apac', 'workstation-08', 'Altair Radioss', 'radioss', '2024.0', 'alice.chen@workstation-08', '2026-01-30 07:00:00', 2, 'APAC-SG', 60, 44),
('Altair', 'APAC', 'bob.wilson', 'license-server-apac', 'workstation-08', 'Altair Radioss', 'radioss', '2024.0', 'bob.wilson@workstation-08', '2026-01-29 08:00:00', 3, 'APAC-SG', 60, 39),
('MSC', 'EU', 'admin', 'license-server-eu', 'server-01', 'MSC Nastran', 'nastran', '2024.1', 'admin@server-01', '2026-01-30 05:30:00', 5, 'HQ', 100, 55),
('Particleworks', 'APAC', 'bob.wilson', 'license-server-apac', 'workstation-09', 'Particleworks', 'particleworks', '8.0', 'bob.wilson@workstation-09', '2026-01-30 09:00:00', 1, 'APAC-SG', 10, 7),
('MSC', 'EU', 'john.doe', 'license-server-eu', 'workstation-01', 'MSC Nastran', 'nastran', '2024.1', 'john.doe@workstation-01', '2026-01-28 08:30:00', 2, 'EU-LON', 100, 42),
('MSC', 'EU', 'jane.smith', 'license-server-eu', 'workstation-02', 'MSC Patran', 'patran', '2024.1', 'jane.smith@workstation-02', '2026-01-28 11:00:00', 1, 'EU-LON', 50, 21),
('Altair', 'EU', 'alice.chen', 'license-server-eu', 'workstation-04', 'Altair HyperWorks', 'hyperworks', '2024.0', 'alice.chen@workstation-04', '2026-01-28 12:00:00', 1, 'EU-BER', 75, 35),
('MSC', 'APAC', 'bob.wilson', 'license-server-apac', 'workstation-03', 'MSC Nastran', 'nastran', '2024.1', 'bob.wilson@workstation-03', '2026-01-28 06:30:00', 3, 'APAC-SG', 100, 58),
('Altair', 'AME', 'john.doe', 'license-server-ame', 'workstation-05', 'Altair HyperMesh', 'hypermesh', '2024.0', 'john.doe@workstation-05', '2026-01-28 15:00:00', 2, 'US-NYC', 75, 26);
