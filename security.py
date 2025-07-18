from functools import wraps
from flask import request, current_app, abort, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_security(app):
    """Initialize security features for the application."""
    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Initialize Talisman for security headers
    Talisman(
        app,
        force_https=True,
        strict_transport_security=True,
        session_cookie_secure=True,
        content_security_policy=app.config['SECURITY_HEADERS']['Content-Security-Policy']
    )
    
    # Add security headers middleware
    @app.after_request
    def add_security_headers(response):
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
        return response
    
    return limiter

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
    """Sanitize HTML content to prevent XSS attacks."""
    from bleach import clean
    return clean(html_content, 
                tags=['p', 'br', 'b', 'i', 'u', 'em', 'strong', 'a'],
                attributes={'a': ['href', 'title']},
                strip=True)

def check_rate_limit(limiter, endpoint):
    """Check if request is within rate limits."""
    try:
        limiter.check()
        return True
    except Exception as e:
        log_security_event('rate_limit_exceeded', 
                          f"Endpoint: {endpoint}, IP: {get_remote_address()}")
        return False 