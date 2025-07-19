#!/usr/bin/env python3
"""
Email Configuration Diagnostic Script
Checks the current email service configuration and identifies issues
"""

import os
import sys
from datetime import datetime

def check_email_configuration():
    """Check all email-related configuration settings"""
    
    print("=" * 60)
    print("EMAIL SERVICE CONFIGURATION DIAGNOSTIC")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check for old connection string (should be removed)
    print("🔍 CONNECTION STRING CHECK (Should be empty)")
    print("-" * 40)
    conn_string = os.environ.get('AZURE_EMAIL_CONNECTION_STRING', '')
    if conn_string:
        print("⚠️  WARNING: Connection string still present!")
        print(f"   Length: {len(conn_string)} characters")
        print("   Action: Remove this environment variable")
    else:
        print("✅ Connection string not present (correct)")
    print()
    
    # Check service principal configuration
    print("🔐 SERVICE PRINCIPAL CONFIGURATION")
    print("-" * 40)
    
    required_vars = {
        'AZURE_CLIENT_ID': os.environ.get('AZURE_CLIENT_ID', ''),
        'AZURE_CLIENT_SECRET': os.environ.get('AZURE_CLIENT_SECRET', ''),
        'AZURE_TENANT_ID': os.environ.get('AZURE_TENANT_ID', ''),
        'AZURE_COMMUNICATION_SERVICE_ENDPOINT': os.environ.get('AZURE_COMMUNICATION_SERVICE_ENDPOINT', ''),
        'AZURE_EMAIL_SENDER': os.environ.get('AZURE_EMAIL_SENDER', 'noreply@netrunmail.com')
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if var_value:
            if 'SECRET' in var_name:
                print(f"✅ {var_name}: {'*' * 10} (hidden)")
            elif 'ID' in var_name and len(var_value) > 10:
                print(f"✅ {var_name}: {var_value[:8]}...{var_value[-4:]}")
            else:
                print(f"✅ {var_name}: {var_value}")
        else:
            print(f"❌ {var_name}: NOT SET")
            missing_vars.append(var_name)
    
    print()
    
    # Check endpoint format
    endpoint = os.environ.get('AZURE_COMMUNICATION_SERVICE_ENDPOINT', '')
    if endpoint:
        print("📡 ENDPOINT VALIDATION")
        print("-" * 40)
        if endpoint.startswith('https://') and '.communication.azure.com' in endpoint:
            print("✅ Endpoint format looks correct")
            print(f"   Domain: {endpoint.split('//')[1].split('.')[0]}")
        else:
            print("❌ Endpoint format incorrect!")
            print("   Expected: https://<service-name>.communication.azure.com")
            print(f"   Got: {endpoint}")
    print()
    
    # Summary
    print("📊 CONFIGURATION SUMMARY")
    print("-" * 40)
    
    if missing_vars:
        print("❌ MISSING REQUIRED VARIABLES:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("🔧 To fix:")
        print("1. Go to Azure Portal → App Service → Configuration")
        print("2. Add the missing environment variables")
        print("3. Save and restart the app service")
    else:
        print("✅ All required variables are set")
        print()
        print("🔍 TROUBLESHOOTING STEPS:")
        print("1. Check if service principal has Communication Services permissions")
        print("2. Verify the Communication Service endpoint is correct")
        print("3. Ensure the sender domain is verified in Azure Communication Services")
        print("4. Check application logs for specific error messages")
    
    print()
    
    # Import availability check
    print("📦 PYTHON PACKAGE AVAILABILITY")
    print("-" * 40)
    
    try:
        from azure.communication.email import EmailClient
        print("✅ azure.communication.email is available")
    except ImportError as e:
        print(f"❌ azure.communication.email import failed: {e}")
        print("   Run: pip install azure-communication-email")
    
    try:
        from azure.identity import DefaultAzureCredential
        print("✅ azure.identity is available")
    except ImportError as e:
        print(f"❌ azure.identity import failed: {e}")
        print("   Run: pip install azure-identity")
    
    print()
    
    # Test authentication (if possible)
    print("🧪 AUTHENTICATION TEST")
    print("-" * 40)
    
    if all([required_vars['AZURE_CLIENT_ID'], 
            required_vars['AZURE_CLIENT_SECRET'], 
            required_vars['AZURE_TENANT_ID'],
            required_vars['AZURE_COMMUNICATION_SERVICE_ENDPOINT']]):
        print("Configuration appears complete. Testing authentication...")
        
        try:
            from azure.identity import DefaultAzureCredential
            from azure.communication.email import EmailClient
            
            credential = DefaultAzureCredential()
            client = EmailClient(
                endpoint=required_vars['AZURE_COMMUNICATION_SERVICE_ENDPOINT'],
                credential=credential
            )
            print("✅ EmailClient created successfully")
            print("   Note: This doesn't guarantee email sending will work")
            print("   Check logs for actual email send attempts")
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            print("   This usually means:")
            print("   - Service principal doesn't have required permissions")
            print("   - Endpoint URL is incorrect")
            print("   - Credentials are invalid")
    else:
        print("❌ Cannot test authentication - missing required variables")
    
    print()
    print("📋 NEXT STEPS:")
    print("-" * 40)
    print("1. Fix any missing environment variables")
    print("2. Run: ./setup_service_principal.sh (if permissions not set)")
    print("3. Check Azure App Service logs for detailed errors")
    print("4. Test form submission and monitor logs")
    print("5. Verify email domain is configured in Azure Communication Services")
    print()
    
    # Return status for automated testing
    return len(missing_vars) == 0

if __name__ == '__main__':
    success = check_email_configuration()
    sys.exit(0 if success else 1)