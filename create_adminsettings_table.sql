-- SQL script to create admin_settings table in MySQL database
-- Run this script if migrations fail due to database connection issues

USE dealtrack_db;

CREATE TABLE IF NOT EXISTS `admin_settings` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `allow_new_showroom_registration` tinyint(1) NOT NULL DEFAULT '1',
    `maintenance_mode` tinyint(1) NOT NULL DEFAULT '0',
    `platform_announcement` longtext DEFAULT NULL,
    `max_showrooms_per_user` int(11) NOT NULL DEFAULT '1',
    `email_notifications_enabled` tinyint(1) NOT NULL DEFAULT '1',
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default settings if table is empty
INSERT IGNORE INTO `admin_settings` (
    `id`, 
    `allow_new_showroom_registration`, 
    `maintenance_mode`, 
    `platform_announcement`, 
    `max_showrooms_per_user`, 
    `email_notifications_enabled`,
    `created_at`,
    `updated_at`
) VALUES (
    1, 
    1, 
    0, 
    '', 
    1, 
    1,
    NOW(),
    NOW()
);
