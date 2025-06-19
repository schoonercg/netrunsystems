import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
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

    # Blog configuration
    BLOG_POST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog_posts')

    # Azure Communication Services configuration
    AZURE_COMMUNICATION_SERVICES_CONNECTION_STRING = os.environ.get('AZURE_COMMUNICATION_SERVICES_CONNECTION_STRING', '')
    AZURE_COMMUNICATION_SERVICES_SENDER_EMAIL = os.environ.get('AZURE_COMMUNICATION_SERVICES_SENDER_EMAIL', 'noreply@netrunsystems.com')
    MAIL_DEFAULT_SENDER = 'daniel@netrunsystems.com'
    
    # Azure Entra ID (Azure AD) configuration
    AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID', '')
    AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET', '')
    AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID', '')
    AZURE_AUTHORITY = f'https://login.microsoftonline.com/{os.environ.get("AZURE_TENANT_ID", "")}'
    AZURE_REDIRECT_URI = os.environ.get('AZURE_REDIRECT_URI', '/auth/callback')
    AZURE_SCOPE = ['User.Read']

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class StagingConfig(Config):
    """Staging configuration."""
    DEBUG = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

    # Additional production-specific settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

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