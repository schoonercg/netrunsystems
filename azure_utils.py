from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import logging
import os
from datetime import datetime, timedelta

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
            self.credential = DefaultAzureCredential()
            logger.info("Successfully initialized Azure credentials")
        except Exception as e:
            logger.error(f"Failed to initialize Azure credentials: {str(e)}")
            raise
        
        # Initialize Key Vault client
        try:
            keyvault_url = f"https://{app.config['AZURE_KEYVAULT_NAME']}.vault.azure.net"
            self.keyvault_client = SecretClient(vault_url=keyvault_url, credential=self.credential)
            logger.info("Successfully initialized Key Vault client")
        except Exception as e:
            logger.error(f"Failed to initialize Key Vault client: {str(e)}")
            raise
        
        # Initialize Blob Storage client
        try:
            connection_string = self.get_secret('AZURE_STORAGE_CONNECTION_STRING')
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            logger.info("Successfully initialized Blob Storage client")
        except Exception as e:
            logger.error(f"Failed to initialize Blob Storage client: {str(e)}")
            raise
        
        # Configure Azure Monitor
        try:
            configure_azure_monitor()
            FlaskInstrumentor().instrument_app(app)
            logger.info("Successfully configured Azure Monitor")
        except Exception as e:
            logger.error(f"Failed to configure Azure Monitor: {str(e)}")
            raise
    
    def get_secret(self, secret_name):
        """
        Retrieve a secret from Azure Key Vault using managed identity.
        """
        try:
            secret_client = SecretClient(vault_url="https://netrun-keyvault.vault.azure.net/", credential=self.credential)
            secret = secret_client.get_secret(secret_name)
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