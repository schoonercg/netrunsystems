#!/bin/bash
# Azure Service Principal Setup for Netrunmail
# Run these commands to configure your existing service principal for Azure Communication Services

set -e

echo "🔐 Azure Service Principal Setup for Netrunmail"
echo "================================================"
echo
echo "This script helps you configure your existing service principal for Azure Communication Services."
echo "Make sure you have Azure CLI installed and are logged in with appropriate permissions."
echo

# Check if Azure CLI is available
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "❌ Please log in to Azure CLI first:"
    echo "   az login"
    exit 1
fi

echo "✅ Azure CLI is available and you are logged in."
echo

# Get current subscription
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "📋 Current subscription: $SUBSCRIPTION_ID"
echo

# Prompt for required information
echo "Please provide the following information:"
echo

read -p "🔑 Service Principal Client ID (AZURE_CLIENT_ID): " CLIENT_ID
if [[ -z "$CLIENT_ID" ]]; then
    echo "❌ Client ID is required"
    exit 1
fi

read -p "📧 Communication Service name (e.g., netrunmail): " COMM_SERVICE_NAME
if [[ -z "$COMM_SERVICE_NAME" ]]; then
    echo "❌ Communication Service name is required"
    exit 1
fi

read -p "📦 Resource Group name: " RESOURCE_GROUP
if [[ -z "$RESOURCE_GROUP" ]]; then
    echo "❌ Resource Group is required"
    exit 1
fi

echo
echo "🔍 Verifying resources..."

# Verify service principal exists
if ! az ad sp show --id "$CLIENT_ID" &> /dev/null; then
    echo "❌ Service principal with ID '$CLIENT_ID' not found"
    exit 1
fi

echo "✅ Service principal found: $CLIENT_ID"

# Verify communication service exists
if ! az communication show --name "$COMM_SERVICE_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    echo "❌ Communication service '$COMM_SERVICE_NAME' not found in resource group '$RESOURCE_GROUP'"
    echo "Please create the Azure Communication Service first:"
    echo "   https://docs.microsoft.com/en-us/azure/communication-services/quickstarts/create-communication-resource"
    exit 1
fi

echo "✅ Communication service found: $COMM_SERVICE_NAME"

# Get the communication service resource ID
RESOURCE_ID=$(az communication show --name "$COMM_SERVICE_NAME" --resource-group "$RESOURCE_GROUP" --query id -o tsv)
echo "📋 Resource ID: $RESOURCE_ID"

# Get the communication service endpoint
ENDPOINT=$(az communication show --name "$COMM_SERVICE_NAME" --resource-group "$RESOURCE_GROUP" --query hostName -o tsv)
echo "🌐 Endpoint: https://$ENDPOINT"
echo

echo "🔧 Assigning permissions..."

# Assign Communication Services Contributor role
echo "Adding Communication Services Contributor role..."
if az role assignment create \
    --assignee "$CLIENT_ID" \
    --role "Communication Services Contributor" \
    --scope "$RESOURCE_ID" \
    --output none; then
    echo "✅ Communication Services Contributor role assigned"
else
    echo "⚠️  Role assignment may have failed (might already exist)"
fi

echo
echo "🔍 Verifying role assignment..."
ROLES=$(az role assignment list --assignee "$CLIENT_ID" --scope "$RESOURCE_ID" --query "[].roleDefinitionName" -o tsv)
if [[ -n "$ROLES" ]]; then
    echo "✅ Assigned roles:"
    echo "$ROLES" | sed 's/^/   - /'
else
    echo "❌ No roles found for this service principal on the Communication Service"
    exit 1
fi

echo
echo "🎉 SUCCESS! Service principal configuration complete."
echo
echo "📋 Environment Variables for Deployment:"
echo "========================================"
echo "# Add these to your Azure App Service Configuration:"
echo "AZURE_COMMUNICATION_SERVICE_ENDPOINT=https://$ENDPOINT"
echo "AZURE_EMAIL_SENDER=noreply@$COMM_SERVICE_NAME.com"
echo
echo "# These should already exist:"
echo "AZURE_CLIENT_ID=$CLIENT_ID"
echo "AZURE_CLIENT_SECRET=<your-existing-secret>"
echo "AZURE_TENANT_ID=<your-existing-tenant-id>"
echo
echo "🚀 Next Steps:"
echo "=============="
echo "1. Update your Azure App Service environment variables with the values above"
echo "2. Remove the old AZURE_EMAIL_CONNECTION_STRING variable"
echo "3. Deploy your application"
echo "4. Test email functionality with the forms"
echo "5. Check logs for successful authentication and email sending"
echo
echo "📚 For detailed setup instructions, see:"
echo "   AZURE-SERVICE-PRINCIPAL-SETUP.md"
echo
echo "🧪 To test the configuration, run:"
echo "   python3 test_netrunmail_forms.py"
echo

# Test authentication (optional)
read -p "🧪 Test service principal authentication now? (y/N): " TEST_AUTH
if [[ "$TEST_AUTH" =~ ^[Yy]$ ]]; then
    echo
    echo "Testing authentication..."
    if az communication list --output table; then
        echo "✅ Service principal can access Communication Services"
    else
        echo "❌ Service principal authentication test failed"
    fi
fi

echo
echo "✅ Setup complete! Your service principal is ready for Netrunmail."