-- Update script: Clear and regenerate license history logs
-- Use this to refresh history data on an existing database
-- Run with: python scripts/run_sql.py init-db/update-history-only.sql

USE license_tracker;

-- Clear existing history logs
DELETE FROM license_history_logs;

-- Reset auto increment
ALTER TABLE license_history_logs AUTO_INCREMENT = 1;

-- Source the generator script (this must be run manually or via the run_sql.py script)
-- The generate_license_history procedure will create 2000 new records

-- Drop procedure if exists
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

-- Generate 2000 records (100x the original 20)
CALL generate_license_history(2000);

-- Cleanup
DROP PROCEDURE IF EXISTS generate_license_history;

-- Show result
SELECT CONCAT('License history updated: ', COUNT(*), ' records') AS result FROM license_history_logs;
