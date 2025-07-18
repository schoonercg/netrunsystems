"""WSGI entry point for Azure App Service deployment"""

import sys
import logging

# Configure logging to help diagnose issues
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting WSGI application import...")
    from app import app as application
    logger.info("Flask application imported successfully")
    logger.info(f"Flask app name: {application.name}")
    logger.info("WSGI application ready")
except Exception as e:
    logger.error(f"Failed to import Flask application: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)