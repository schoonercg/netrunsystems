import os

# Azure Entra ID Settings
CLIENT_ID = os.environ.get('AZURE_CLIENT_ID', '')  # Application (client) ID from Azure portal
CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET', '')  # Client secret from Azure portal
TENANT_ID = os.environ.get('AZURE_TENANT_ID', '')  # Directory (tenant) ID from Azure portal
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
REDIRECT_PATH = '/getAToken'  # Used for forming an absolute URL for redirect
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # Microsoft Graph API endpoint

# Flask Session settings
SESSION_TYPE = 'filesystem'

# The scope for the Microsoft Graph API
SCOPE = [
    'User.Read',
    'User.ReadBasic.All',
]

# Session key names
SESS_TOKEN_KEY = 'token_cache'
SESS_USER_KEY = 'user' 