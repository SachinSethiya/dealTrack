#!/usr/bin/env python
"""
Test script to verify AdminSettings import fix
"""
import os
import sys
import django
from django.conf import settings

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dealTrack.settings')
django.setup()

def test_adminsettings_import():
    """Test that AdminSettings can be imported successfully"""
    try:
        from super_admin.models import AdminSettings
        print("✅ AdminSettings model imported successfully")
        
        # Test the get_settings method
        settings = AdminSettings.get_settings()
        print(f"✅ AdminSettings.get_settings() works: {settings}")
        
        # Test form import
        from super_admin.forms import AdminSettingsForm
        print("✅ AdminSettingsForm imported successfully")
        
        # Test form instantiation
        form = AdminSettingsForm(instance=settings)
        print(f"✅ AdminSettingsForm instantiated: {form}")
        
        return True
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing AdminSettings import fix...")
    success = test_adminsettings_import()
    
    if success:
        print("\n🎉 All imports successful! The NameError has been fixed.")
    else:
        print("\n❌ Import test failed. Check the error messages above.")
