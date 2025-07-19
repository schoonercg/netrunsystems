# Azure Service Principal Setup for Netrunmail

## Overview

This guide shows how to configure the existing Azure service principal to work with Azure Communication Services (Netrunmail) using best practices instead of connection strings.

## Current Service Principal

The application already uses a service principal with these environment variables:
- `AZURE_CLIENT_ID` - Service principal application ID
- `AZURE_CLIENT_SECRET` - Service principal secret
- `AZURE_TENANT_ID` - Azure AD tenant ID

## Required Azure Communication Services Permissions

### 1. Add Communication Services Permissions

The existing service principal needs these additional permissions:

#### Azure Communication Services Roles
```bash
# Communication Services Contributor (for sending emails)
az role assignment create \
    --assignee <AZURE_CLIENT_ID> \
    --role "Communication Services Contributor" \
    --scope "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.Communication/communicationServices/<COMMUNICATION_SERVICE_NAME>"
```

#### Alternative: Communication Services Data Contributor
```bash
# More specific role for data operations
az role assignment create \
    --assignee <AZURE_CLIENT_ID> \
    --role "Communication Services Data Contributor" \
    --scope "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>/providers/Microsoft.Communication/communicationServices/<COMMUNICATION_SERVICE_NAME>"
```

### 2. Required Environment Variables

Update your deployment to use service principal authentication:

#### Remove (Connection String - Not Secure)
```bash
# ❌ Remove this - less secure
AZURE_EMAIL_CONNECTION_STRING=
```

#### Add (Service Principal - Secure)
```bash
# ✅ Use these instead - more secure
AZURE_COMMUNICATION_SERVICE_ENDPOINT=https://<your-service>.communication.azure.com
AZURE_EMAIL_SENDER=noreply@netrunmail.com

# ✅ These should already exist from current service principal
AZURE_CLIENT_ID=<existing-service-principal-id>
AZURE_CLIENT_SECRET=<existing-service-principal-secret>
AZURE_TENANT_ID=<existing-tenant-id>
```

## Azure CLI Setup Commands

### Step 1: Get Current Service Principal Info
```bash
# List current service principals
az ad sp list --display-name "<your-app-name>" --query "[].{DisplayName:displayName, AppId:appId, ObjectId:id}"
```

### Step 2: Get Communication Service Info
```bash
# Get your Communication Service details
az communication list --query "[].{Name:name, Location:location, Endpoint:hostName}"

# Get the full resource ID
az communication show --name "<communication-service-name>" --resource-group "<resource-group>" --query "id"
```

### Step 3: Assign Permissions
```bash
# Option A: Communication Services Contributor (broad permissions)
az role assignment create \
    --assignee "<AZURE_CLIENT_ID>" \
    --role "Communication Services Contributor" \
    --scope "<COMMUNICATION_SERVICE_RESOURCE_ID>"

# Option B: Communication Services Data Contributor (data-only permissions)
az role assignment create \
    --assignee "<AZURE_CLIENT_ID>" \
    --role "Communication Services Data Contributor" \
    --scope "<COMMUNICATION_SERVICE_RESOURCE_ID>"
```

### Step 4: Verify Permissions
```bash
# Check assigned roles
az role assignment list --assignee "<AZURE_CLIENT_ID>" --query "[].{Role:roleDefinitionName, Scope:scope}"
```

## Application Changes Made

### 1. Updated Authentication Method
- **Before**: Connection string authentication
- **After**: Service principal with `DefaultAzureCredential`

### 2. New Configuration
```python
# Service principal authentication
credential = DefaultAzureCredential()
email_client = EmailClient(endpoint=AZURE_COMMUNICATION_SERVICE_ENDPOINT, credential=credential)
```

### 3. Environment Variables
```python
# Required for service principal
AZURE_COMMUNICATION_SERVICE_ENDPOINT = os.environ.get('AZURE_COMMUNICATION_SERVICE_ENDPOINT', '')
AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID', '')        # Existing
AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET', '') # Existing  
AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID', '')        # Existing
```

## Security Benefits

### ✅ Service Principal Advantages
- **No connection strings** - More secure credential management
- **Role-based access** - Granular permissions
- **Audit logging** - Better tracking of access
- **Centralized management** - Single service principal for all Azure services
- **Rotation support** - Easier credential rotation
- **Principle of least privilege** - Only necessary permissions

### ❌ Connection String Disadvantages
- **Embedded secrets** - Connection strings contain sensitive data
- **Harder to rotate** - Manual process to update connection strings
- **Less granular** - Broader access than needed
- **Audit gaps** - Less detailed logging

## Deployment Configuration

### Azure App Service Configuration

In Azure Portal → App Service → Configuration → Application Settings:

```bash
# Communication Service Settings
AZURE_COMMUNICATION_SERVICE_ENDPOINT=https://netrunmail.communication.azure.com
AZURE_EMAIL_SENDER=noreply@netrunmail.com

# Service Principal (should already exist)
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>  
AZURE_TENANT_ID=<your-tenant-id>
```

### GitHub Actions Secrets

Update your GitHub repository secrets:

```bash
# Add new secret
AZURE_COMMUNICATION_SERVICE_ENDPOINT=https://netrunmail.communication.azure.com

# Keep existing secrets
AZURE_CLIENT_ID=<existing>
AZURE_CLIENT_SECRET=<existing>
AZURE_TENANT_ID=<existing>
```

## Testing the Configuration

### 1. Check Service Principal Permissions
```bash
# Test Azure CLI access with service principal
az login --service-principal \
    --username "<AZURE_CLIENT_ID>" \
    --password "<AZURE_CLIENT_SECRET>" \
    --tenant "<AZURE_TENANT_ID>"

# Test Communication Services access
az communication list
```

### 2. Test Application
```python
# Use the debug endpoint to verify configuration
GET /debug

# Expected response should show:
{
    "config": {
        "azure_service_principal": true,
        "netrunmail_service_endpoint": true,
        "azure_identity_available": true
    }
}
```

### 3. Test Email Functionality
- Submit forms to test email sending
- Check Azure App Service logs for success messages:
  - `✅ Netrunmail email sent successfully`
  - Look for Message ID in logs

## Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Error: The client does not have authorization to perform action
# Solution: Add proper role assignment
az role assignment create --assignee "<AZURE_CLIENT_ID>" --role "Communication Services Contributor" --scope "<RESOURCE_ID>"
```

#### 2. Endpoint Not Found
```bash
# Error: Could not resolve host
# Solution: Check endpoint format
AZURE_COMMUNICATION_SERVICE_ENDPOINT=https://<service-name>.communication.azure.com
```

#### 3. Authentication Failed
```bash
# Error: Authentication failed
# Solution: Verify service principal credentials
az ad sp show --id "<AZURE_CLIENT_ID>"
```

## Required Azure Resources

### 1. Azure Communication Services
- **Service Name**: netrunmail (or your chosen name)
- **Domain**: netrunmail.com (must be verified)
- **Email Domain**: Configured and verified

### 2. Service Principal Roles
- **Communication Services Contributor** OR
- **Communication Services Data Contributor**

### 3. Email Domain Verification
- **DNS Records**: SPF, DKIM, DMARC configured
- **Domain Verification**: Completed in Azure portal
- **Sender Verification**: noreply@netrunmail.com verified

## Next Steps

1. **Update Environment Variables** in Azure App Service
2. **Assign Service Principal Permissions** using Azure CLI
3. **Test Email Functionality** with all forms
4. **Remove Connection String** environment variable
5. **Monitor Logs** for successful authentication and email sending

---

**Security Note**: Using service principals with `DefaultAzureCredential` follows Azure security best practices and is recommended for production environments.

**Last Updated**: July 19, 2025  
**Status**: ✅ Ready for deployment