# Email Service Troubleshooting Guide

## 🚨 Common Issues and Solutions

### Issue: No emails being received from form submissions

This guide helps you diagnose and fix email delivery issues with the Netrunmail service.

## 🔍 Quick Diagnostics

### 1. Check Configuration on Dev Slot

Run the diagnostic script locally or on the server:
```bash
python3 debug_email_config.py
```

### 2. Check Azure App Service Logs

Use the provided script to check logs:
```bash
./check_email_logs.sh
# Enter: netrun (app name)
# Enter: <your-resource-group>
# Enter: dev (slot name)
```

### 3. Common Configuration Issues

#### ❌ Issue: Old Connection String Still Present
**Symptom**: `AZURE_EMAIL_CONNECTION_STRING` environment variable exists  
**Solution**: 
```bash
# Remove the old connection string
az webapp config appsettings delete \
    --name netrun \
    --resource-group <resource-group> \
    --slot dev \
    --setting-names AZURE_EMAIL_CONNECTION_STRING
```

#### ❌ Issue: Missing Service Endpoint
**Symptom**: `AZURE_COMMUNICATION_SERVICE_ENDPOINT` not set  
**Solution**:
```bash
# Add the endpoint
az webapp config appsettings set \
    --name netrun \
    --resource-group <resource-group> \
    --slot dev \
    --settings AZURE_COMMUNICATION_SERVICE_ENDPOINT=https://netrunmail.communication.azure.com
```

#### ❌ Issue: Service Principal Not Configured
**Symptom**: Missing `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, or `AZURE_TENANT_ID`  
**Solution**: These should already exist from your deployment. If missing:
```bash
# Check existing service principal settings
az webapp config appsettings list \
    --name netrun \
    --resource-group <resource-group> \
    --slot dev \
    --query "[?contains(name, 'AZURE_CLIENT')].{name:name}" \
    -o table
```

#### ❌ Issue: No Permissions on Communication Service
**Symptom**: Authentication errors in logs (401, 403)  
**Solution**: Run the setup script to add permissions:
```bash
./setup_service_principal.sh
```

## 📋 Complete Configuration Checklist

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_COMMUNICATION_SERVICE_ENDPOINT` | Communication service URL | `https://netrunmail.communication.azure.com` |
| `AZURE_EMAIL_SENDER` | Sender email address | `noreply@netrunmail.com` |
| `AZURE_CLIENT_ID` | Service principal ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_CLIENT_SECRET` | Service principal secret | `<secret-value>` |
| `AZURE_TENANT_ID` | Azure AD tenant ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |

### Should NOT Exist
| Variable | Description | Action |
|----------|-------------|--------|
| `AZURE_EMAIL_CONNECTION_STRING` | Old connection string | Remove this |

## 🧪 Testing Email Functionality

### Option 1: Add Test Endpoint (Recommended)

1. Add the test endpoint from `email_test_endpoint.py` to your `app.py`
2. Deploy the changes
3. Visit: `https://netrun-dev-[id].azurewebsites.net/test-email-config`
4. To send a test email: `https://netrun-dev-[id].azurewebsites.net/test-email-config?send_test=true&email=your@email.com`

### Option 2: Manual Form Test

1. Go to any form (e.g., `/early-access`)
2. Submit the form
3. Check logs immediately:
```bash
az webapp log tail \
    --name netrun \
    --resource-group <resource-group> \
    --slot dev \
    --filter Email
```

## 🔍 Log Messages to Look For

### ✅ Success Messages
- `✅ Netrunmail email sent successfully to [email]. Message ID: [id]`
- `Sending email via Netrunmail service principal from noreply@netrunmail.com`
- `Email service configured with sender: noreply@netrunmail.com`

### ❌ Error Messages
- `Service principal credentials not configured for Netrunmail`
- `Netrunmail service endpoint not configured`
- `Netrunmail Azure Communication Email or Identity not available`
- `Authentication failed`
- `The client does not have authorization`

## 🛠️ Step-by-Step Troubleshooting

### Step 1: Verify Current Configuration
```bash
# List all email-related settings
az webapp config appsettings list \
    --name netrun \
    --resource-group <resource-group> \
    --slot dev \
    --query "[?contains(name, 'AZURE')].{name:name}" \
    -o table
```

### Step 2: Check Service Principal Permissions
```bash
# Get service principal ID
CLIENT_ID=$(az webapp config appsettings list \
    --name netrun \
    --resource-group <resource-group> \
    --slot dev \
    --query "[?name=='AZURE_CLIENT_ID'].value" \
    -o tsv)

# Check assigned roles
az role assignment list \
    --assignee $CLIENT_ID \
    --query "[?contains(scope, 'communicationServices')].{Role:roleDefinitionName, Scope:scope}" \
    -o table
```

### Step 3: Verify Communication Service
```bash
# List communication services
az communication list \
    --query "[].{Name:name, Endpoint:hostName}" \
    -o table
```

### Step 4: Test Authentication
```bash
# Try to authenticate with service principal
az login --service-principal \
    -u <AZURE_CLIENT_ID> \
    -p <AZURE_CLIENT_SECRET> \
    --tenant <AZURE_TENANT_ID>

# Test access to communication service
az communication list
```

## 🚀 Quick Fix Script

Create and run this script to fix common issues:

```bash
#!/bin/bash
# quick_fix_email.sh

APP_NAME="netrun"
SLOT_NAME="dev"
RESOURCE_GROUP="<your-resource-group>"
COMM_SERVICE_ENDPOINT="https://netrunmail.communication.azure.com"

echo "🔧 Fixing email configuration..."

# Remove old connection string
echo "Removing old connection string..."
az webapp config appsettings delete \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --setting-names AZURE_EMAIL_CONNECTION_STRING 2>/dev/null

# Add new endpoint
echo "Adding communication service endpoint..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME \
    --settings \
    AZURE_COMMUNICATION_SERVICE_ENDPOINT=$COMM_SERVICE_ENDPOINT \
    AZURE_EMAIL_SENDER=noreply@netrunmail.com

# Restart the app
echo "Restarting app service..."
az webapp restart \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --slot $SLOT_NAME

echo "✅ Configuration updated! Test email functionality now."
```

## 📊 Monitoring Email Delivery

### Real-time Log Monitoring
```bash
# Watch for email-related logs
az webapp log tail \
    --name netrun \
    --resource-group <resource-group> \
    --slot dev | grep -E "(email|Email|✅|❌|Netrunmail)"
```

### Check Application Insights
1. Go to Azure Portal → Application Insights
2. Search for: `traces | where message contains "email"`
3. Look for success/failure patterns

## 🔐 Security Checklist

- [ ] Connection string removed (`AZURE_EMAIL_CONNECTION_STRING`)
- [ ] Service principal has only necessary permissions
- [ ] Email domain verified in Azure Communication Services
- [ ] SPF/DKIM records configured for domain

## 📞 Need More Help?

1. **Check Azure Communication Services Status**: Portal → Communication Service → Overview
2. **Verify Domain**: Portal → Communication Service → Email → Domains
3. **Review Quotas**: Portal → Communication Service → Usage + quotas
4. **Check Service Health**: https://status.azure.com

---

**Last Updated**: July 19, 2025  
**Common Fix**: Usually missing `AZURE_COMMUNICATION_SERVICE_ENDPOINT` or old connection string still present