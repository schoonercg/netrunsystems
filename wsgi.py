"""WSGI entry point for Azure App Service deployment"""

import sys
import os
import logging

# Configure logging to help diagnose issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting WSGI application import...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    from app import app as application
    
    logger.info("Flask application imported successfully")
    logger.info(f"Flask app name: {application.name}")
    logger.info(f"Flask routes registered: {len(application.url_map._rules)}")
    logger.info("WSGI application ready")
    
    # Test a route to make sure the app is working
    with application.test_client() as client:
        response = client.get('/health')
        logger.info(f"Health check test: {response.status}")
        
except Exception as e:
    logger.error(f"Failed to import Flask application: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Ensure application is available at module level
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Running Flask development server on port {port}")
    application.run(host='0.0.0.0', port=port, debug=False)