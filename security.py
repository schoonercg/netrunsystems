from functools import wraps
from flask import request, current_app, abort, session, redirect, url_for
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_security(app):
    """Initialize basic security features for the application."""
    
    # Add basic security headers middleware
    @app.after_request
    def add_security_headers(response):
        # Basic security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block'
        }
        for header, value in security_headers.items():
            response.headers[header] = value
        return response
    
    logger.info("Basic security headers initialized")
    return None

def require_azure_ad(f):
    """Decorator to require Azure AD authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get('AZURE_AD_CLIENT_ID'):
            logger.error("Azure AD configuration missing")
            abort(500)
        
        # Check if user is authenticated
        if not session.get('user'):
            logger.warning(f"Unauthorized access attempt to {request.path}")
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def log_security_event(event_type, details):
    """Log security-related events."""
    logger.info(f"Security Event: {event_type} - {details} - {datetime.utcnow()}")

def validate_input(data, rules):
    """Validate input data against security rules."""
    for field, rule in rules.items():
        if field in data:
            if not rule(data[field]):
                log_security_event('input_validation_failed', 
                                 f"Field: {field}, Value: {data[field]}")
                return False
    return True

def sanitize_html(html_content):
    """Basic HTML sanitization to prevent XSS attacks."""
    # Simple HTML escaping since bleach is not available
    import html
    return html.escape(html_content)

def check_rate_limit(limiter, endpoint):
    """Check if request is within rate limits."""
    # Basic rate limiting not available without flask-limiter
    # This is a placeholder for when rate limiting is needed
    return True 