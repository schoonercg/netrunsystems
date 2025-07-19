#!/usr/bin/env python
"""Minimal test to isolate the worker crash issue"""

import sys
import os
import logging

# Basic logging setup
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger('minimal_test')

logger.info("=== MINIMAL TEST START ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"PORT: {os.environ.get('PORT', 'not set')}")

try:
    logger.info("Step 1: Testing basic Flask import...")
    import flask
    logger.info("✓ Flask imported")
    
    logger.info("Step 2: Creating minimal Flask app...")
    app = flask.Flask(__name__)
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200
    
    logger.info("✓ Minimal Flask app created")
    
    logger.info("Step 3: Testing gunicorn import...")
    from gunicorn.app.base import BaseApplication
    logger.info("✓ Gunicorn imported")
    
    logger.info("Step 4: Starting gunicorn with minimal app...")
    
    class MinimalApplication(BaseApplication):
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
        'timeout': 30,
        'accesslog': '-',
        'errorlog': '-',
        'loglevel': 'info',
    }
    
    logger.info(f"✓ Starting minimal gunicorn on {options['bind']}")
    MinimalApplication(app, options).run()
    
except Exception as e:
    logger.error(f"MINIMAL TEST FAILED: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)