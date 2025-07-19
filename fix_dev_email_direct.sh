#!/bin/bash
# Direct Azure CLI commands to fix email configuration on dev slot

echo "🔧 Direct Email Configuration Fix for Dev Slot"
echo "=============================================="
echo
echo "Run these commands one by one to fix your dev slot email configuration:"
echo

# Step 1: Copy service principal credentials from production to dev slot
echo "# Step 1: Copy service principal credentials from production to dev"
echo "# Replace <RESOURCE_GROUP> with your actual resource group name"
echo
echo "# Get credentials from production slot:"
echo 'AZURE_CLIENT_ID=$(az webapp config appsettings list --name netrun --resource-group <RESOURCE_GROUP> --query "[?name=='"'"'AZURE_CLIENT_ID'"'"'].value" -o tsv)'
echo 'AZURE_CLIENT_SECRET=$(az webapp config appsettings list --name netrun --resource-group <RESOURCE_GROUP> --query "[?name=='"'"'AZURE_CLIENT_SECRET'"'"'].value" -o tsv)'
echo 'AZURE_TENANT_ID=$(az webapp config appsettings list --name netrun --resource-group <RESOURCE_GROUP> --query "[?name=='"'"'AZURE_TENANT_ID'"'"'].value" -o tsv)'
echo
echo "# Verify they were retrieved:"
echo 'echo "Client ID: ${AZURE_CLIENT_ID:0:8}..."'
echo 'echo "Tenant ID: ${AZURE_TENANT_ID:0:8}..."'
echo 'echo "Secret set: $([ -n "$AZURE_CLIENT_SECRET" ] && echo "Yes" || echo "No")"'
echo

# Step 2: Set all email configuration on dev slot
echo "# Step 2: Set all email configuration on dev slot"
echo 'az webapp config appsettings set \'
echo '    --name netrun \'
echo '    --resource-group <RESOURCE_GROUP> \'
echo '    --slot dev \'
echo '    --settings \'
echo '    AZURE_CLIENT_ID="$AZURE_CLIENT_ID" \'
echo '    AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET" \'
echo '    AZURE_TENANT_ID="$AZURE_TENANT_ID" \'
echo '    AZURE_COMMUNICATION_SERVICE_ENDPOINT="https://netrunmail.communication.azure.com" \'
echo '    AZURE_EMAIL_SENDER="noreply@netrunmail.com"'
echo

# Step 3: Remove old connection string
echo "# Step 3: Remove old connection string (if it exists)"
echo 'az webapp config appsettings delete \'
echo '    --name netrun \'
echo '    --resource-group <RESOURCE_GROUP> \'
echo '    --slot dev \'
echo '    --setting-names AZURE_EMAIL_CONNECTION_STRING'
echo

# Step 4: Restart the app
echo "# Step 4: Restart the dev slot"
echo 'az webapp restart \'
echo '    --name netrun \'
echo '    --resource-group <RESOURCE_GROUP> \'
echo '    --slot dev'
echo

# Step 5: Verify configuration
echo "# Step 5: Verify the configuration"
echo 'az webapp config appsettings list \'
echo '    --name netrun \'
echo '    --resource-group <RESOURCE_GROUP> \'
echo '    --slot dev \'
echo '    --query "[?contains(name, '"'"'AZURE_EMAIL'"'"') || contains(name, '"'"'AZURE_COMMUNICATION'"'"') || contains(name, '"'"'AZURE_CLIENT'"'"') || contains(name, '"'"'AZURE_TENANT'"'"')].{name:name}" \'
echo '    -o table'
echo
echo "# Test the email configuration"
echo "# Visit: https://netrun-dev.azurewebsites.net/test-email-config"
echo "# Send test: https://netrun-dev.azurewebsites.net/test-email-config?send_test=true&email=your@email.com"
echo
echo "# Monitor logs:"
echo 'az webapp log tail \'
echo '    --name netrun \'
echo '    --resource-group <RESOURCE_GROUP> \'
echo '    --slot dev \'
echo '    --filter Email'