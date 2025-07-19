#!/usr/bin/env python
"""Azure startup wrapper with enhanced error logging"""

import sys
import os
import logging

# Set up logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('startup')

logger.info("=== Azure App Service Startup ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"PORT environment variable: {os.environ.get('PORT', 'not set')}")

try:
    logger.info("Attempting to import Flask app...")
    from app import app as application
    logger.info("✓ Flask app imported successfully")
    
    # Run with gunicorn programmatically
    logger.info("Starting gunicorn...")
    
    from gunicorn.app.base import BaseApplication
    
    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()
            
        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)
                
        def load(self):
            return self.application
    
    options = {
        'bind': f"0.0.0.0:{os.environ.get('PORT', '8000')}",
        'workers': 1,
        'timeout': 600,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'info',
    }
    
    logger.info(f"Gunicorn binding to: {options['bind']}")
    StandaloneApplication(application, options).run()
    
except Exception as e:
    logger.error(f"STARTUP FAILED: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)