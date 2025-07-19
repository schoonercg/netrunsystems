#!/bin/bash
# Comprehensive email configuration deployment script for Azure App Service

echo "🚀 Azure Email Service Configuration Deployment"
echo "==============================================="
echo
echo "This script will configure your dev slot with all required email settings."
echo

# Default configuration
APP_NAME="netrun"
SLOT_NAME="dev"
COMM_SERVICE_ENDPOINT="https://netrunmail.communication.azure.com"
EMAIL_SENDER="noreply@netrunmail.com"

# Get resource group from user
read -p "📦 Enter your Resource Group name: " RESOURCE_GROUP

if [[ -z "$RESOURCE_GROUP" ]]; then
    echo "❌ Resource Group is required"
    exit 1
fi

# Check Azure CLI
if ! az account show &> /dev/null; then
    echo "❌ Please log in to Azure CLI first:"
    echo "   az login"
    exit 1
fi

echo "✅ Azure CLI authenticated"
echo

# Step 1: Get service principal credentials from production slot
echo "📋 Step 1: Copying service principal credentials from production..."

# Get credentials from production slot
echo "Getting service principal settings from production slot..."

AZURE_CLIENT_ID=$(az webapp config appsettings list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[?name=='AZURE_CLIENT_ID'].value" \
    -o tsv 2>/dev/null)

AZURE_CLIENT_SECRET=$(az webapp config appsettings list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[?name=='AZURE_CLIENT_SECRET'].value" \
    -o tsv 2>/dev/null)

AZURE_TENANT_ID=$(az webapp config appsettings list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "[?name=='AZURE_TENANT_ID'].value" \
    -o tsv 2>/dev/null)

# Check if we got the credentials
if [[ -z "$AZURE_CLIENT_ID" || -z "$AZURE_CLIENT_SECRET" || -z "$AZURE_TENANT_ID" ]]; then
    echo "❌ Could not retrieve service principal credentials from production slot."
    echo "   Please ensure these are set in your production configuration:"
    echo "   - AZURE_CLIENT_ID"
    echo "   - AZURE_CLIENT_SECRET" 
    echo "   - AZURE_TENANT_ID"
    echo
    echo "🔧 Manual Setup Required:"
    echo "   1. Go to Azure Portal → App Service → Configuration"
    echo "   2. Copy these settings from production to dev slot"
    echo "   3. Re-run this script"
    exit 1
fi

echo "✅ Retrieved service principal credentials from production"

# Step 2: Remove old connection string if it exists
echo
echo "📋 Step 2: Cleaning up old configuration..."

az webapp config appsettings delete \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --setting-names AZURE_EMAIL_CONNECTION_STRING 2>/dev/null || true

echo "✅ Old connection string removed (if it existed)"

# Step 3: Set all required email configuration
echo
echo "📋 Step 3: Setting email service configuration..."

az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --settings \
    AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \
    AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \
    AZURE_TENANT_ID="$AZURE_TENANT_ID" \
    AZURE_COMMUNICATION_SERVICE_ENDPOINT="$COMM_SERVICE_ENDPOINT" \
    AZURE_EMAIL_SENDER="$EMAIL_SENDER" \
    --output none

echo "✅ Email service configuration deployed to dev slot"

# Step 4: Install required Python packages
echo
echo "📋 Step 4: Installing required Python packages..."

# Create a requirements file for the missing packages
cat > /tmp/email_requirements.txt << EOF
azure-communication-email>=1.0.0
azure-identity>=1.12.0
EOF

# Deploy the requirements (this may require a deployment)
echo "📦 Required packages for email service:"
echo "   - azure-communication-email>=1.0.0"
echo "   - azure-identity>=1.12.0"
echo
echo "⚠️  IMPORTANT: These packages need to be added to your requirements.txt"
echo "   and deployed through your normal deployment process."

# Step 5: Restart the app service
echo
echo "📋 Step 5: Restarting app service..."

az webapp restart \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME

echo "✅ App service restarted"

# Step 6: Verify configuration
echo
echo "📋 Step 6: Verifying configuration..."

# Wait a moment for restart
sleep 5

echo "Current email-related configuration on dev slot:"
az webapp config appsettings list \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --query "[?contains(name, 'AZURE_EMAIL') || contains(name, 'AZURE_COMMUNICATION') || contains(name, 'AZURE_CLIENT') || contains(name, 'AZURE_TENANT')].{name:name}" \
    -o table 2>/dev/null

echo
echo "🎉 Email Configuration Deployment Complete!"
echo
echo "📋 Next Steps:"
echo "=============="
echo "1. Update your requirements.txt to include:"
echo "   azure-communication-email>=1.0.0"
echo "   azure-identity>=1.12.0"
echo
echo "2. Deploy your application with updated requirements"
echo
echo "3. Test the configuration:"
echo "   https://$APP_NAME-$SLOT_NAME.azurewebsites.net/test-email-config"
echo
echo "4. Send a test email:"
echo "   https://$APP_NAME-$SLOT_NAME.azurewebsites.net/test-email-config?send_test=true&email=your@email.com"
echo
echo "5. Monitor logs:"
echo "   az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP --slot $SLOT_NAME --filter Email"
echo
echo "📚 If you still have issues, check:"
echo "   - Ensure packages are deployed: pip list | grep azure-communication"
echo "   - Run: ./setup_service_principal.sh (if permission errors)"
echo "   - Review: EMAIL-TROUBLESHOOTING.md"
echo