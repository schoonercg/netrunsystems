"""
Main entry point for Azure App Service deployment.
This file ensures proper initialization and startup for the Flask application.
"""

import os
import sys
import logging

# Configure logging for Azure App Service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    # Import the Flask application
    from app import app
    
    # Ensure we have the application object available for Azure App Service
    application = app
    
    logger.info("Flask application initialized successfully")
    
    if __name__ == "__main__":
        # Get port from environment variable (Azure App Service sets this)
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"Starting Flask application on port {port}")
        
        # Run the application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False
        )
        
except Exception as e:
    logger.error(f"Failed to initialize Flask application: {str(e)}")
    sys.exit(1)