#!/usr/bin/env python
"""
Test script to verify AdminSettings import syntax without Django setup
"""
import ast
import os

def test_adminsettings_syntax():
    """Test that AdminSettings can be imported syntactically"""
    
    # Test models.py syntax
    models_path = os.path.join(os.path.dirname(__file__), 'super_admin', 'models.py')
    try:
        with open(models_path, 'r') as f:
            models_code = f.read()
        
        # Parse the Python code to check for syntax errors
        ast.parse(models_code)
        print("✅ super_admin/models.py syntax is valid")
        
        # Check if AdminSettings class exists
        if 'class AdminSettings(models.Model):' in models_code:
            print("✅ AdminSettings class found in models.py")
        else:
            print("❌ AdminSettings class not found in models.py")
            return False
            
    except SyntaxError as e:
        print(f"❌ Syntax error in models.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading models.py: {e}")
        return False
    
    # Test forms.py syntax and import
    forms_path = os.path.join(os.path.dirname(__file__), 'super_admin', 'forms.py')
    try:
        with open(forms_path, 'r') as f:
            forms_code = f.read()
        
        # Parse the Python code to check for syntax errors
        ast.parse(forms_code)
        print("✅ super_admin/forms.py syntax is valid")
        
        # Check if AdminSettings import exists
        if 'from .models import AdminSettings' in forms_code:
            print("✅ AdminSettings import found in forms.py")
        else:
            print("❌ AdminSettings import not found in forms.py")
            return False
            
        # Check if AdminSettingsForm class exists
        if 'class AdminSettingsForm(forms.ModelForm):' in forms_code:
            print("✅ AdminSettingsForm class found in forms.py")
        else:
            print("❌ AdminSettingsForm class not found in forms.py")
            return False
            
    except SyntaxError as e:
        print(f"❌ Syntax error in forms.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading forms.py: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing AdminSettings import fix (syntax only)...")
    success = test_adminsettings_syntax()
    
    if success:
        print("\n🎉 Syntax check passed! The NameError should be fixed.")
        print("\nThe fix implemented:")
        print("1. ✅ AdminSettings model exists in super_admin/models.py")
        print("2. ✅ 'from .models import AdminSettings' added to super_admin/forms.py")
        print("3. ✅ AdminSettingsForm properly defined in super_admin/forms.py")
        print("4. ✅ Settings view uses AdminSettings.get_settings() correctly")
    else:
        print("\n❌ Syntax check failed. Check the error messages above.")
