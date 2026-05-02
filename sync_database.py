#!/usr/bin/env python
"""
Database synchronization script for DealTrack Django project.
This script handles database table creation and migration issues.
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.core.exceptions import OperationalError

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealTrack.settings')
    django.setup()

def check_database_connection():
    """Check if database connection works"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            return cursor.fetchone() is not None
    except OperationalError:
        return False

def create_adminsettings_table():
    """Create admin_settings table using raw SQL"""
    try:
        with connection.cursor() as cursor:
            create_table_sql = """
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
            """
            cursor.execute(create_table_sql)
            
            # Insert default settings if table is empty
            cursor.execute("""
                INSERT IGNORE INTO `admin_settings` (
                    `id`, `allow_new_showroom_registration`, `maintenance_mode`, 
                    `platform_announcement`, `max_showrooms_per_user`, 
                    `email_notifications_enabled`, `created_at`, `updated_at`
                ) VALUES (1, 1, 0, '', 1, 1, NOW(), NOW())
            """)
            
        print("✅ admin_settings table created successfully")
        return True
    except OperationalError as e:
        print(f"❌ Failed to create admin_settings table: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    try:
        print("🔄 Running Django migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_initial_migration():
    """Create initial migration for super_admin app"""
    try:
        print("🔄 Creating initial migration for super_admin...")
        execute_from_command_line(['manage.py', 'makemigrations', 'super_admin'])
        print("✅ Initial migration created successfully")
        return True
    except Exception as e:
        print(f"❌ Migration creation failed: {e}")
        return False

def check_all_models():
    """Check if all model tables exist"""
    from django.apps import apps
    
    all_models = apps.get_models()
    missing_tables = []
    
    for model in all_models:
        table_name = model._meta.db_table
        if not check_table_exists(table_name):
            missing_tables.append(table_name)
    
    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False
    else:
        print("✅ All model tables exist")
        return True

def main():
    """Main sync function"""
    print("🚀 Starting DealTrack database synchronization...")
    
    # Setup Django
    setup_django()
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        return False
    
    # Check if admin_settings table exists
    if not check_table_exists('admin_settings'):
        print("⚠️  admin_settings table missing, creating...")
        if not create_adminsettings_table():
            return False
    else:
        print("✅ admin_settings table exists")
    
    # Try to create migrations
    try:
        create_initial_migration()
    except:
        print("⚠️  Migration creation failed, continuing...")
    
    # Try to run migrations
    try:
        run_migrations()
    except:
        print("⚠️  Migration failed, checking tables manually...")
    
    # Check all model tables
    if check_all_models():
        print("🎉 Database synchronization completed successfully!")
        return True
    else:
        print("⚠️  Some tables may still be missing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
