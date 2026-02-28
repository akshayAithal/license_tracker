-- Create dashboard-related tables for customizable dashboard, denials, and realtime usage snapshots
USE license_tracker;

-- Dashboard layouts per user (Grafana-like customizable widgets)
CREATE TABLE IF NOT EXISTS dashboard_layouts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    layout_name VARCHAR(64) DEFAULT 'default',
    layout_json TEXT NOT NULL,
    is_default BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_layout (user_id, layout_name),
    FOREIGN KEY (user_id) REFERENCES local_users(id) ON DELETE CASCADE
);

-- License denials tracking
CREATE TABLE IF NOT EXISTS license_denials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application VARCHAR(16),
    region VARCHAR(16),
    user VARCHAR(64) NOT NULL,
    host VARCHAR(64),
    feature VARCHAR(64),
    reason VARCHAR(255),
    denied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_license INT,
    total_license_used INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_denied_at (denied_at),
    INDEX idx_app_region (application, region)
);

-- Realtime usage snapshots (taken every 5 minutes by scheduler)
CREATE TABLE IF NOT EXISTS realtime_usage_snapshots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application VARCHAR(16) NOT NULL,
    region VARCHAR(16),
    feature VARCHAR(64),
    total_license INT,
    used_license INT,
    snapshot_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_snapshot_time (snapshot_time),
    INDEX idx_app_feature (application, feature)
);

-- Generate initial denial data (last 30 days)
DROP PROCEDURE IF EXISTS generate_denial_data;

DELIMITER //

CREATE PROCEDURE generate_denial_data(IN num_records INT)
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE app VARCHAR(16);
    DECLARE region VARCHAR(16);
    DECLARE username VARCHAR(64);
    DECLARE host VARCHAR(64);
    DECLARE feature VARCHAR(64);
    DECLARE reason VARCHAR(255);
    DECLARE total_lic INT;
    DECLARE total_used INT;
    DECLARE dt DATETIME;
    DECLARE app_idx INT;
    DECLARE user_idx INT;
    DECLARE reason_idx INT;
    
    WHILE i < num_records DO
        SET app_idx = FLOOR(1 + RAND() * 4);
        
        CASE app_idx
            WHEN 1 THEN 
                SET app = 'MSC';
                SET feature = ELT(FLOOR(1 + RAND() * 3), 'nastran', 'patran', 'marc');
                SET total_lic = CASE feature WHEN 'nastran' THEN 100 WHEN 'patran' THEN 50 ELSE 40 END;
            WHEN 2 THEN 
                SET app = 'Altair';
                SET feature = ELT(FLOOR(1 + RAND() * 3), 'hyperworks', 'hypermesh', 'radioss');
                SET total_lic = CASE feature WHEN 'radioss' THEN 60 ELSE 75 END;
            WHEN 3 THEN 
                SET app = 'RLM';
                SET feature = 'masta';
                SET total_lic = 25;
            ELSE 
                SET app = 'Particleworks';
                SET feature = 'particleworks';
                SET total_lic = 10;
        END CASE;
        
        SET region = ELT(FLOOR(1 + RAND() * 3), 'EU', 'APAC', 'AME');
        SET total_used = total_lic;
        
        SET user_idx = FLOOR(1 + RAND() * 10);
        CASE user_idx
            WHEN 1 THEN SET username = 'john.doe'; SET host = 'workstation-01';
            WHEN 2 THEN SET username = 'jane.smith'; SET host = 'workstation-02';
            WHEN 3 THEN SET username = 'bob.wilson'; SET host = 'workstation-03';
            WHEN 4 THEN SET username = 'alice.chen'; SET host = 'workstation-04';
            WHEN 5 THEN SET username = 'admin'; SET host = 'server-01';
            WHEN 6 THEN SET username = 'mike.jones'; SET host = 'workstation-10';
            WHEN 7 THEN SET username = 'sarah.lee'; SET host = 'workstation-11';
            WHEN 8 THEN SET username = 'david.kim'; SET host = 'workstation-12';
            WHEN 9 THEN SET username = 'emma.white'; SET host = 'workstation-13';
            ELSE SET username = 'chris.brown'; SET host = 'workstation-14';
        END CASE;
        
        SET reason_idx = FLOOR(1 + RAND() * 4);
        CASE reason_idx
            WHEN 1 THEN SET reason = 'All licenses in use';
            WHEN 2 THEN SET reason = 'License server unreachable';
            WHEN 3 THEN SET reason = 'Feature not available in license pool';
            ELSE SET reason = 'Maximum user limit reached';
        END CASE;
        
        SET dt = DATE_SUB(NOW(), INTERVAL FLOOR(RAND() * 30) DAY) - INTERVAL FLOOR(RAND() * 24) HOUR - INTERVAL FLOOR(RAND() * 60) MINUTE;
        
        INSERT INTO license_denials (application, region, user, host, feature, reason, denied_at, total_license, total_license_used)
        VALUES (app, region, username, host, feature, reason, dt, total_lic, total_used);
        
        SET i = i + 1;
    END WHILE;
END //

DELIMITER ;

CALL generate_denial_data(200);
DROP PROCEDURE IF EXISTS generate_denial_data;

-- Generate initial realtime usage snapshots (last 24 hours, every 5 min = 288 snapshots)
DROP PROCEDURE IF EXISTS generate_usage_snapshots;

DELIMITER //

CREATE PROCEDURE generate_usage_snapshots()
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE total_snapshots INT DEFAULT 288;
    DECLARE snapshot_dt DATETIME;
    DECLARE base_used INT;
    DECLARE variation INT;
    
    WHILE i < total_snapshots DO
        SET snapshot_dt = DATE_SUB(NOW(), INTERVAL (total_snapshots - i) * 5 MINUTE);
        
        -- MSC Nastran
        SET base_used = 40 + FLOOR(RAND() * 30);
        INSERT INTO realtime_usage_snapshots (application, region, feature, total_license, used_license, snapshot_time)
        VALUES ('MSC', 'EU', 'nastran', 100, LEAST(base_used, 100), snapshot_dt);
        
        -- MSC Patran
        SET base_used = 15 + FLOOR(RAND() * 20);
        INSERT INTO realtime_usage_snapshots (application, region, feature, total_license, used_license, snapshot_time)
        VALUES ('MSC', 'EU', 'patran', 50, LEAST(base_used, 50), snapshot_dt);
        
        -- Altair HyperWorks
        SET base_used = 30 + FLOOR(RAND() * 25);
        INSERT INTO realtime_usage_snapshots (application, region, feature, total_license, used_license, snapshot_time)
        VALUES ('Altair', 'EU', 'hyperworks', 75, LEAST(base_used, 75), snapshot_dt);
        
        -- Altair HyperMesh
        SET base_used = 25 + FLOOR(RAND() * 20);
        INSERT INTO realtime_usage_snapshots (application, region, feature, total_license, used_license, snapshot_time)
        VALUES ('Altair', 'APAC', 'hypermesh', 75, LEAST(base_used, 75), snapshot_dt);
        
        -- RLM MASTA
        SET base_used = 5 + FLOOR(RAND() * 12);
        INSERT INTO realtime_usage_snapshots (application, region, feature, total_license, used_license, snapshot_time)
        VALUES ('RLM', 'EU', 'masta', 25, LEAST(base_used, 25), snapshot_dt);
        
        -- Particleworks
        SET base_used = 2 + FLOOR(RAND() * 5);
        INSERT INTO realtime_usage_snapshots (application, region, feature, total_license, used_license, snapshot_time)
        VALUES ('Particleworks', 'APAC', 'particleworks', 10, LEAST(base_used, 10), snapshot_dt);
        
        SET i = i + 1;
    END WHILE;
END //

DELIMITER ;

CALL generate_usage_snapshots();
DROP PROCEDURE IF EXISTS generate_usage_snapshots;

-- Insert default dashboard layout for admin user
INSERT INTO dashboard_layouts (user_id, layout_name, layout_json, is_default) VALUES
(1, 'default', '[{"id":"expiry_alert","span":10,"label":"Expiry Alert"},{"id":"realtime_usage","span":8,"label":"Real Time Usage"},{"id":"denials","span":6,"label":"Denials"},{"id":"heatmap","span":24,"label":"Heat Map"}]', TRUE);
