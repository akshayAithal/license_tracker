-- Create database schema for license_tracker

USE license_tracker;

-- User types enum equivalent
CREATE TABLE IF NOT EXISTS local_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255),
    type ENUM('ADMIN', 'USER') DEFAULT 'USER',
    site_code VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Application settings table (for LDAP config and other settings)
CREATE TABLE IF NOT EXISTS app_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(64) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(32) DEFAULT 'string',
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- License details table (active/live checkouts)
-- When a license is checked back in, the record moves to license_history_logs
CREATE TABLE IF NOT EXISTS license_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    application VARCHAR(16),
    region VARCHAR(16),
    user VARCHAR(64) NOT NULL,
    host VARCHAR(64),
    feature VARCHAR(64),
    user_key VARCHAR(64),
    license_used INT,
    site_code VARCHAR(16),
    check_out DATETIME,
    check_in DATETIME,
    spent_hours VARCHAR(16),
    total_license INT,
    total_license_used INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_active_checkouts (check_in, application, feature),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES local_users(id) ON DELETE SET NULL
);

-- License history logs table (completed usage after check-in)
-- Records are moved here from license_details when a license is checked back in
CREATE TABLE IF NOT EXISTS license_history_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    application VARCHAR(16),
    region VARCHAR(16),
    user VARCHAR(64) NOT NULL,
    server VARCHAR(64),
    host VARCHAR(64),
    software VARCHAR(64),
    feature VARCHAR(64),
    version VARCHAR(64),
    user_key VARCHAR(64),
    date_time DATETIME,
    check_out DATETIME,
    check_in DATETIME,
    spent_hours VARCHAR(16),
    license_used INT,
    site_code VARCHAR(16),
    total_license INT,
    total_license_used INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_history_user_id (user_id),
    INDEX idx_history_datetime (date_time),
    INDEX idx_history_app_feature (application, feature),
    FOREIGN KEY (user_id) REFERENCES local_users(id) ON DELETE SET NULL
);

-- Alembic version table for Flask-Migrate
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
