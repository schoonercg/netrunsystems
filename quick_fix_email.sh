#!/bin/bash
# Quick fix script for email configuration issues on dev slot

echo "🔧 Azure Email Service Quick Fix Script"
echo "======================================"
echo
echo "This script will fix common email configuration issues on your dev slot."
echo

# Configuration
APP_NAME="netrun"
SLOT_NAME="dev"
COMM_SERVICE_ENDPOINT="https://netrunmail.communication.azure.com"
EMAIL_SENDER="noreply@netrunmail.com"

# Prompt for resource group
read -p "📦 Enter your Resource Group name: " RESOURCE_GROUP

if [[ -z "$RESOURCE_GROUP" ]]; then
    echo "❌ Resource Group is required"
    exit 1
fi

echo
echo "🔍 Checking current configuration..."

# Check if logged in to Azure CLI
if ! az account show &> /dev/null; then
    echo "❌ Please log in to Azure CLI first:"
    echo "   az login"
    exit 1
fi

echo "✅ Azure CLI authenticated"
echo

# Step 1: Check and remove old connection string
echo "📋 Step 1: Checking for old connection string..."
if az webapp config appsettings list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --query "[?name=='AZURE_EMAIL_CONNECTION_STRING']" \
    -o tsv 2>/dev/null | grep -q .; then
    
    echo "⚠️  Found old connection string. Removing..."
    az webapp config appsettings delete \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --slot $SLOT_NAME \
        --setting-names AZURE_EMAIL_CONNECTION_STRING
    echo "✅ Old connection string removed"
else
    echo "✅ No old connection string found (good)"
fi

echo
echo "📋 Step 2: Checking service principal configuration..."

# Check if service principal vars exist
SP_VARS_EXIST=true
for var in AZURE_CLIENT_ID AZURE_CLIENT_SECRET AZURE_TENANT_ID; do
    if ! az webapp config appsettings list \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --slot $SLOT_NAME \
        --query "[?name=='$var']" \
        -o tsv 2>/dev/null | grep -q .; then
        echo "❌ Missing: $var"
        SP_VARS_EXIST=false
    else
        echo "✅ Found: $var"
    fi
done

if [ "$SP_VARS_EXIST" = false ]; then
    echo
    echo "❌ Service principal variables are missing!"
    echo "   These should be inherited from your main deployment."
    echo "   Please check your App Service configuration."
    exit 1
fi

echo
echo "📋 Step 3: Setting Communication Service endpoint..."

# Set the communication service endpoint
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --settings \
    AZURE_COMMUNICATION_SERVICE_ENDPOINT=$COMM_SERVICE_ENDPOINT \
    AZURE_EMAIL_SENDER=$EMAIL_SENDER \
    --output none

echo "✅ Communication service endpoint configured"

echo
echo "📋 Step 4: Verifying configuration..."

# List all email-related settings
echo "Current email configuration:"
az webapp config appsettings list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --query "[?contains(name, 'AZURE_EMAIL') || contains(name, 'AZURE_COMMUNICATION')].{name:name}" \
    -o table

echo
echo "📋 Step 5: Restarting the app service..."

# Restart the app
az webapp restart \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME

echo "✅ App service restarted"

echo
echo "🎉 Configuration update complete!"
echo
echo "📧 Test Email Functionality:"
echo "============================"
echo "1. Visit your dev site and submit a form"
echo "2. Monitor logs with this command:"
echo
echo "az webapp log tail \\"
echo "    --name $APP_NAME \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --slot $SLOT_NAME \\"
echo "    --filter Email"
echo
echo "3. Look for these success messages:"
echo "   ✅ 'Netrunmail email sent successfully'"
echo "   ✅ 'Message ID: <uuid>'"
echo
echo "❌ If you see these errors:"
echo "   - 'Service principal credentials not configured' → Re-run this script"
echo "   - 'Authentication failed' → Run ./setup_service_principal.sh"
echo "   - 'Invalid sender' → Check domain verification in Azure"
echo
echo "📚 For more help, see EMAIL-TROUBLESHOOTING.md"