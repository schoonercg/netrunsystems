#!/usr/bin/env python3
"""
Startup script for Azure Web App deployment.
This ensures the application starts correctly in Azure App Service.
"""

import os
import sys
from app import app as application

if __name__ == "__main__":
    # For Azure App Service, we need to bind to 0.0.0.0 and use the PORT environment variable
    port = int(os.environ.get('PORT', 8000))
    application.run(host='0.0.0.0', port=port, debug=False)