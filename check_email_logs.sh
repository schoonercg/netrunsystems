#!/bin/bash
# Script to check Azure App Service logs for email-related issues

echo "🔍 Azure App Service Email Log Checker"
echo "======================================"
echo
echo "This script helps you check logs for email service issues."
echo

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Get app service details
read -p "📱 App Service name (e.g., netrun): " APP_NAME
read -p "📦 Resource Group name: " RESOURCE_GROUP
read -p "🎰 Deployment slot (e.g., dev, or leave empty for production): " SLOT_NAME

echo
echo "📊 Checking logs for email-related messages..."
echo

# Construct the app name with slot if provided
if [[ -n "$SLOT_NAME" ]]; then
    FULL_APP_NAME="$APP_NAME/slots/$SLOT_NAME"
    echo "Checking slot: $SLOT_NAME"
else
    FULL_APP_NAME="$APP_NAME"
    echo "Checking production slot"
fi

echo
echo "🔍 Recent email-related log entries:"
echo "===================================="

# Stream logs and filter for email-related messages
echo "Fetching last 100 log entries..."
az webapp log show \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    $([ -n "$SLOT_NAME" ] && echo "--slot $SLOT_NAME") \
    --query "properties.recentLogs" \
    -o tsv | grep -E -i "(email|netrunmail|communication|send_email|✅|❌|AZURE_COMMUNICATION_SERVICE|AZURE_EMAIL)" | tail -50

echo
echo "📋 Common Email Error Patterns to Look For:"
echo "=========================================="
echo "1. 'Service principal credentials not configured for Netrunmail'"
echo "   → Missing AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, or AZURE_TENANT_ID"
echo
echo "2. 'Netrunmail service endpoint not configured'"
echo "   → Missing AZURE_COMMUNICATION_SERVICE_ENDPOINT"
echo
echo "3. 'Authentication failed' or '401'"
echo "   → Service principal lacks Communication Services permissions"
echo
echo "4. 'Invalid sender' or 'Sender not verified'"
echo "   → Email domain not verified in Azure Communication Services"
echo
echo "5. 'Connection refused' or 'Could not resolve host'"
echo "   → Incorrect endpoint URL format"
echo

# Check current configuration
echo "🔧 Checking current configuration..."
echo "===================================="

# Get app settings (filtered for email-related)
echo "Email-related environment variables:"
az webapp config appsettings list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    $([ -n "$SLOT_NAME" ] && echo "--slot $SLOT_NAME") \
    --query "[?contains(name, 'AZURE_EMAIL') || contains(name, 'AZURE_COMMUNICATION') || contains(name, 'AZURE_CLIENT') || contains(name, 'AZURE_TENANT')].{name:name, value:value}" \
    -o table 2>/dev/null | while read line; do
        if [[ "$line" == *"SECRET"* ]] || [[ "$line" == *"CONNECTION_STRING"* ]]; then
            # Hide sensitive values
            echo "$line" | sed 's/\(SECRET\|CONNECTION_STRING\).*$/\1    ***HIDDEN***/g'
        else
            echo "$line"
        fi
    done

echo
echo "🚨 Quick Diagnostics:"
echo "===================="

# Check if old connection string exists
if az webapp config appsettings list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    $([ -n "$SLOT_NAME" ] && echo "--slot $SLOT_NAME") \
    --query "[?name=='AZURE_EMAIL_CONNECTION_STRING']" \
    -o tsv &>/dev/null | grep -q .; then
    echo "⚠️  WARNING: Old AZURE_EMAIL_CONNECTION_STRING still exists!"
    echo "   Action: Remove this and use service principal instead"
else
    echo "✅ Old connection string not found (good)"
fi

# Check if new endpoint exists
if az webapp config appsettings list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    $([ -n "$SLOT_NAME" ] && echo "--slot $SLOT_NAME") \
    --query "[?name=='AZURE_COMMUNICATION_SERVICE_ENDPOINT']" \
    -o tsv &>/dev/null | grep -q .; then
    echo "✅ AZURE_COMMUNICATION_SERVICE_ENDPOINT is configured"
else
    echo "❌ AZURE_COMMUNICATION_SERVICE_ENDPOINT is missing!"
    echo "   Action: Add this environment variable"
fi

echo
echo "📱 To stream live logs:"
echo "======================"
echo "az webapp log tail \\"
echo "    --name $APP_NAME \\"
echo "    --resource-group $RESOURCE_GROUP \\"
if [[ -n "$SLOT_NAME" ]]; then
    echo "    --slot $SLOT_NAME \\"
fi
echo "    --filter Email"
echo
echo "🔧 To update configuration:"
echo "=========================="
echo "az webapp config appsettings set \\"
echo "    --name $APP_NAME \\"
echo "    --resource-group $RESOURCE_GROUP \\"
if [[ -n "$SLOT_NAME" ]]; then
    echo "    --slot $SLOT_NAME \\"
fi
echo "    --settings AZURE_COMMUNICATION_SERVICE_ENDPOINT=https://netrunmail.communication.azure.com"
echo
echo "📚 For more troubleshooting, see:"
echo "   - AZURE-SERVICE-PRINCIPAL-SETUP.md"
echo "   - Run: python3 debug_email_config.py (on the server)"
echo