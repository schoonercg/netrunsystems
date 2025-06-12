import os
from datetime import timedelta
from azure_manager import get_secret

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for Flask application")
    
    # Azure Web Apps specific settings
    WEBSITE_HOSTNAME = os.environ.get('WEBSITE_HOSTNAME', 'localhost:5000')
    WEBSITE_SITE_NAME = os.environ.get('WEBSITE_SITE_NAME', 'netrun-staging')
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    }
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Blog configuration
    BLOG_POST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog_posts')
    
    # Azure AD configuration
    AZURE_AD_CLIENT_ID = get_secret("AZURE-AD-CLIENT-ID")
    AZURE_AD_CLIENT_SECRET = get_secret("AZURE-AD-CLIENT-SECRET")
    AZURE_AD_TENANT_ID = get_secret("AZURE-AD-TENANT-ID")
    
    # Email configuration
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = get_secret("EMAIL-USER")
    MAIL_PASSWORD = get_secret("EMAIL-PASSWORD")
    MAIL_DEFAULT_SENDER = 'daniel@netrunsystems.com'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    RATELIMIT_ENABLED = False

class StagingConfig(Config):
    """Staging configuration."""
    DEBUG = False
    RATELIMIT_ENABLED = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    RATELIMIT_ENABLED = True
    
    # Additional production-specific settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default']) 