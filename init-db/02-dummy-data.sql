-- Insert dummy data for license_tracker
-- EXPANDED VERSION: 2000 license history records (100x original)

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

-- Insert dummy license history logs (2000 records - 100x expansion)
-- This uses a stored procedure to generate random data spanning 365 days
-- Apps: MSC (nastran, patran, marc), Altair (hyperworks, hypermesh, radioss), RLM (masta), Particleworks

DROP PROCEDURE IF EXISTS generate_license_history;

DELIMITER //

CREATE PROCEDURE generate_license_history(IN num_records INT)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE app VARCHAR(16);
    DECLARE region VARCHAR(16);
    DECLARE username VARCHAR(64);
    DECLARE server VARCHAR(64);
    DECLARE host VARCHAR(64);
    DECLARE software VARCHAR(64);
    DECLARE feature VARCHAR(64);
    DECLARE version VARCHAR(64);
    DECLARE user_key VARCHAR(64);
    DECLARE site_code VARCHAR(16);
    DECLARE total_lic INT;
    DECLARE total_used INT;
    DECLARE lic_used INT;
    DECLARE dt DATETIME;
    DECLARE app_idx INT;
    DECLARE user_idx INT;
    DECLARE feature_idx INT;
    DECLARE days_ago INT;
    DECLARE hours_offset INT;
    
    WHILE i < num_records DO
        SET app_idx = FLOOR(1 + RAND() * 4);
        
        CASE app_idx
            WHEN 1 THEN 
                SET app = 'MSC';
                SET feature_idx = FLOOR(1 + RAND() * 3);
                CASE feature_idx
                    WHEN 1 THEN SET software = 'MSC Nastran'; SET feature = 'nastran'; SET version = '2024.1'; SET total_lic = 100;
                    WHEN 2 THEN SET software = 'MSC Patran'; SET feature = 'patran'; SET version = '2024.1'; SET total_lic = 50;
                    ELSE SET software = 'MSC Marc'; SET feature = 'marc'; SET version = '2024.1'; SET total_lic = 40;
                END CASE;
            WHEN 2 THEN 
                SET app = 'Altair';
                SET feature_idx = FLOOR(1 + RAND() * 3);
                CASE feature_idx
                    WHEN 1 THEN SET software = 'Altair HyperWorks'; SET feature = 'hyperworks'; SET version = '2024.0'; SET total_lic = 75;
                    WHEN 2 THEN SET software = 'Altair HyperMesh'; SET feature = 'hypermesh'; SET version = '2024.0'; SET total_lic = 75;
                    ELSE SET software = 'Altair Radioss'; SET feature = 'radioss'; SET version = '2024.0'; SET total_lic = 60;
                END CASE;
            WHEN 3 THEN 
                SET app = 'RLM';
                SET software = 'MASTA'; SET feature = 'masta'; SET version = '12.0'; SET total_lic = 25;
            ELSE 
                SET app = 'Particleworks';
                SET software = 'Particleworks'; SET feature = 'particleworks'; SET version = '8.0'; SET total_lic = 10;
        END CASE;
        
        SET region = ELT(FLOOR(1 + RAND() * 3), 'EU', 'APAC', 'AME');
        SET server = CONCAT('license-server-', LOWER(region));
        
        SET user_idx = FLOOR(1 + RAND() * 10);
        CASE user_idx
            WHEN 1 THEN SET username = 'john.doe'; SET host = 'workstation-01'; SET site_code = 'EU-LON';
            WHEN 2 THEN SET username = 'jane.smith'; SET host = 'workstation-02'; SET site_code = 'US-NYC';
            WHEN 3 THEN SET username = 'bob.wilson'; SET host = 'workstation-03'; SET site_code = 'APAC-SG';
            WHEN 4 THEN SET username = 'alice.chen'; SET host = 'workstation-04'; SET site_code = 'EU-BER';
            WHEN 5 THEN SET username = 'admin'; SET host = 'server-01'; SET site_code = 'HQ';
            WHEN 6 THEN SET username = 'mike.jones'; SET host = 'workstation-10'; SET site_code = 'US-NYC';
            WHEN 7 THEN SET username = 'sarah.lee'; SET host = 'workstation-11'; SET site_code = 'APAC-SG';
            WHEN 8 THEN SET username = 'david.kim'; SET host = 'workstation-12'; SET site_code = 'EU-LON';
            WHEN 9 THEN SET username = 'emma.white'; SET host = 'workstation-13'; SET site_code = 'US-NYC';
            ELSE SET username = 'chris.brown'; SET host = 'workstation-14'; SET site_code = 'EU-BER';
        END CASE;
        
        SET user_key = CONCAT(username, '@', host);
        SET days_ago = FLOOR(RAND() * 365);
        SET hours_offset = FLOOR(RAND() * 24);
        SET dt = DATE_SUB(NOW(), INTERVAL days_ago DAY) - INTERVAL hours_offset HOUR;
        SET lic_used = FLOOR(1 + RAND() * 5);
        SET total_used = FLOOR(total_lic * 0.2 + RAND() * total_lic * 0.7);
        
        INSERT INTO license_history_logs 
            (application, region, user, server, host, software, feature, version, user_key, date_time, license_used, site_code, total_license, total_license_used)
        VALUES 
            (app, region, username, server, host, software, feature, version, user_key, dt, lic_used, site_code, total_lic, total_used);
        
        SET i = i + 1;
    END WHILE;
END //

DELIMITER ;

-- Generate 2000 license history records (100x the original 20)
CALL generate_license_history(2000);

-- Cleanup procedure
DROP PROCEDURE IF EXISTS generate_license_history;
