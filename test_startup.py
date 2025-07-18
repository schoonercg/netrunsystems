#!/usr/bin/env python3
"""
Simple test to verify basic app structure and imports
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test that the basic Python imports work"""
    try:
        import os
        import re
        import datetime
        import logging
        import sys
        from functools import wraps
        print("✓ Basic Python imports successful")
        return True
    except ImportError as e:
        print(f"✗ Basic imports failed: {e}")
        return False

def test_app_structure():
    """Test that the app file has proper structure"""
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            'app = Flask(__name__)',
            'application = app',
            'if __name__ == \'__main__\'',
            'logger.info',
            'def health_check',
            'def debug_info',
        ]
        
        for check in checks:
            if check in content:
                print(f"✓ Found: {check}")
            else:
                print(f"✗ Missing: {check}")
                return False
        
        print("✓ App structure looks correct")
        return True
    except Exception as e:
        print(f"✗ App structure test failed: {e}")
        return False

def test_requirements():
    """Test that requirements.txt is properly formatted"""
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        
        # Check for key dependencies
        required_deps = [
            'Flask==',
            'gunicorn==',
            'azure-communication-email==',
            'msal==',
            'markdown==',
        ]
        
        content = ''.join(lines)
        for dep in required_deps:
            if dep in content:
                print(f"✓ Found dependency: {dep}")
            else:
                print(f"✗ Missing dependency: {dep}")
                return False
        
        print("✓ Requirements.txt looks correct")
        return True
    except Exception as e:
        print(f"✗ Requirements test failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing Flask app startup readiness...")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_app_structure,
        test_requirements,
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
        print()
    
    if all_passed:
        print("✓ All tests passed! App should be deployment-ready.")
    else:
        print("✗ Some tests failed. Check the issues above.")
    
    sys.exit(0 if all_passed else 1)