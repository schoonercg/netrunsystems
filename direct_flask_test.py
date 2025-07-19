#!/usr/bin/env python
"""Ultra-minimal Flask test - bypass gunicorn entirely"""

import os
import sys

print("=== DIRECT FLASK TEST ===")
print(f"Python version: {sys.version}")
print(f"PORT: {os.environ.get('PORT', 'not set')}")

try:
    import flask
    print("✓ Flask imported")
    
    app = flask.Flask(__name__)
    
    @app.route('/')
    def home():
        return "Direct Flask Test Working!"
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200
    
    print("✓ Flask app created")
    
    port = int(os.environ.get('PORT', 8000))
    print(f"✓ Starting Flask dev server on port {port}")
    
    # Use Flask's built-in development server instead of gunicorn
    app.run(host='0.0.0.0', port=port, debug=False)
    
except Exception as e:
    print(f"✗ DIRECT FLASK TEST FAILED: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)