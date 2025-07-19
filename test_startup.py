#!/usr/bin/env python
"""Test startup to diagnose worker crashes"""

import sys
import os

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Python path:", sys.path)

try:
    print("\n1. Testing basic imports...")
    import flask
    print("   ✓ Flask imported")
    
    print("\n2. Testing app import...")
    from app import app
    print("   ✓ App imported successfully")
    print("   App name:", app.name)
    
    print("\n3. Testing WSGI exposure...")
    from app import application
    print("   ✓ Application exposed")
    
    print("\n4. Testing routes...")
    rules = list(app.url_map.iter_rules())
    print(f"   ✓ {len(rules)} routes registered")
    
    print("\n5. Testing health endpoint...")
    with app.test_client() as client:
        response = client.get('/health')
        print(f"   ✓ Health check: {response.status}")
        
    print("\n✓ ALL TESTS PASSED - App should start successfully")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)