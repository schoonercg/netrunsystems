import logging
import os
from datetime import datetime, timedelta

# Optional Azure imports with graceful fallback
try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    from azure.storage.blob import BlobServiceClient
    AZURE_SERVICES_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Azure services available")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Azure advanced services not available, using basic functionality only")
    DefaultAzureCredential = None
    SecretClient = None
    BlobServiceClient = None
    AZURE_SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)

class AzureServiceManager:
    """Manages Azure service connections and operations."""
    
    def __init__(self, app=None):
        self.app = app
        self.credential = None
        self.keyvault_client = None
        self.blob_service_client = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Azure services with Flask app."""
        self.app = app
        
        # Initialize Azure credentials
        try:
            if AZURE_SERVICES_AVAILABLE and DefaultAzureCredential:
                self.credential = DefaultAzureCredential()
                logger.info("Successfully initialized Azure credentials")
            else:
                logger.info("Azure services not available, skipping credential initialization")
                self.credential = None
        except Exception as e:
            logger.warning(f"Failed to initialize Azure credentials: {str(e)}")
            self.credential = None
        
        # Initialize Key Vault client
        try:
            keyvault_name = app.config.get('AZURE_KEYVAULT_NAME')
            if AZURE_SERVICES_AVAILABLE and keyvault_name and self.credential and SecretClient:
                keyvault_url = f"https://{keyvault_name}.vault.azure.net"
                self.keyvault_client = SecretClient(vault_url=keyvault_url, credential=self.credential)
                logger.info("Successfully initialized Key Vault client")
            else:
                logger.info("Key Vault not available, skipping initialization")
                self.keyvault_client = None
        except Exception as e:
            logger.warning(f"Failed to initialize Key Vault client: {str(e)}")
            self.keyvault_client = None
        
        # Initialize Blob Storage client
        try:
            if AZURE_SERVICES_AVAILABLE and self.keyvault_client and BlobServiceClient:
                connection_string = self.get_secret('AZURE_STORAGE_CONNECTION_STRING')
                if connection_string:
                    self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
                    logger.info("Successfully initialized Blob Storage client")
                else:
                    logger.info("Blob Storage connection string not available")
                    self.blob_service_client = None
            else:
                logger.info("Blob Storage not available, skipping initialization")
                self.blob_service_client = None
        except Exception as e:
            logger.warning(f"Failed to initialize Blob Storage client: {str(e)}")
            self.blob_service_client = None
        
        # Skip Azure Monitor as it's not essential and causing conflicts
        logger.info("Azure Monitor integration skipped to avoid dependency conflicts")
    
    def get_secret(self, secret_name):
        """
        Retrieve a secret from Azure Key Vault using managed identity.
        """
        try:
            if not self.keyvault_client or not self.credential:
                logger.warning(f"Key Vault client not available, cannot retrieve secret {secret_name}")
                return None
            
            secret = self.keyvault_client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Error retrieving secret {secret_name}: {e}")
            return None
    
    def upload_blob(self, container_name, blob_name, data):
        """Upload data to Azure Blob Storage."""
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            logger.info(f"Successfully uploaded blob {blob_name} to container {container_name}")
        except Exception as e:
            logger.error(f"Failed to upload blob {blob_name}: {str(e)}")
            raise
    
    def download_blob(self, container_name, blob_name):
        """Download data from Azure Blob Storage."""
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Failed to download blob {blob_name}: {str(e)}")
            raise
    
    def get_blob_url(self, container_name, blob_name, expiry_hours=24):
        """Generate a SAS URL for a blob."""
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            sas_token = blob_client.generate_shared_access_signature(
                permission="r",
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            return f"{blob_client.url}?{sas_token}"
        except Exception as e:
            logger.error(f"Failed to generate blob URL for {blob_name}: {str(e)}")
            raise

# Initialize the Azure service manager
azure_manager = AzureServiceManager() 