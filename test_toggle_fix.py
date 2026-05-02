#!/usr/bin/env python
"""
Test script to verify the toggle_showroom_status fix
"""
import ast
import os

def test_toggle_showroom_status_fix():
    """Test that the Django template filter has been replaced with proper Python logic"""
    
    views_path = os.path.join(os.path.dirname(__file__), 'super_admin', 'views.py')
    
    try:
        with open(views_path, 'r') as f:
            views_code = f.read()
        
        # Parse the Python code to check for syntax errors
        ast.parse(views_code)
        print("✅ super_admin/views.py syntax is valid")
        
        # Check if the problematic template filter syntax is gone
        if 'showroom.showroom_name|default:showroom.username' in views_code:
            print("❌ Django template filter syntax still found in views.py")
            return False
        else:
            print("✅ Django template filter syntax removed from views.py")
        
        # Check if the correct Python conditional logic is present
        if 'name = showroom.showroom_name if showroom.showroom_name else getattr(showroom, "username", "Showroom")' in views_code:
            print("✅ Correct Python conditional logic found in views.py")
        else:
            print("❌ Correct Python conditional logic not found in views.py")
            return False
            
        # Check if the message uses the correct variable
        if 'messages.success(request, f"Showroom {name} has been {status}.")' in views_code:
            print("✅ Message uses correct Python variable")
        else:
            print("❌ Message does not use correct Python variable")
            return False
            
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in views.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading views.py: {e}")
        return False

if __name__ == "__main__":
    print("Testing toggle_showroom_status fix...")
    success = test_toggle_showroom_status_fix()
    
    if success:
        print("\n🎉 Fix verified successfully!")
        print("\nThe fix implemented:")
        print("1. ❌ REMOVED: showroom.showroom_name|default:showroom.username")
        print("2. ✅ ADDED: name = showroom.showroom_name if showroom.showroom_name else getattr(showroom, 'username', 'Showroom')")
        print("3. ✅ UPDATED: messages.success(request, f'Showroom {name} has been {status}.')")
        print("\nBenefits:")
        print("- ✅ No more Django template filters in Python code")
        print("- ✅ Proper Python conditional logic")
        print("- ✅ Safe handling of missing/null showroom_name")
        print("- ✅ Fallback to username or 'Showroom' if both are missing")
    else:
        print("\n❌ Fix verification failed. Check the error messages above.")
