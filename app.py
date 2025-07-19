
import os
import re
import datetime
import logging
import sys
from functools import wraps

# Configure logging for Azure App Service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import Flask and core dependencies
try:
    from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, session
    from flask_wtf import CSRFProtect
    logger.info("Flask core imports successful")
except ImportError as e:
    logger.error(f"Failed to import Flask core: {e}")
    sys.exit(1)

# Import optional dependencies with graceful fallback
try:
    import markdown
    logger.info("Markdown import successful")
except ImportError:
    logger.warning("Markdown not available, blog functionality will be limited")
    markdown = None

try:
    import msal
    logger.info("MSAL import successful")
except ImportError:
    logger.warning("MSAL not available, Azure AD authentication will be disabled")
    msal = None

try:
    import requests
    logger.info("Requests import successful")
except ImportError:
    logger.warning("Requests not available, some features may be limited")
    requests = None

try:
    from azure.communication.email import EmailClient
    from azure.identity import DefaultAzureCredential
    logger.info("Azure Communication Email and Identity imports successful")
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:
    logger.warning("Azure Communication Email or Identity not available, email functionality will be disabled")
    EmailClient = None
    DefaultAzureCredential = None
    AZURE_IDENTITY_AVAILABLE = False

# Development mode flag
DEV_MODE = os.environ.get('FLASK_ENV') == 'development'

logger.info("Starting Flask application initialization")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'netrun-development-key')

logger.info("Flask app created successfully")

# Azure AD Configuration
AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID', '')
AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET', '')
AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID', '')
AZURE_AUTHORITY = f'https://login.microsoftonline.com/{AZURE_TENANT_ID}'
AZURE_SCOPE = ['User.Read']
AZURE_REDIRECT_PATH = '/getAToken'

# Netrunmail Azure Communication Service Configuration (Service Principal)
AZURE_COMMUNICATION_SERVICE_ENDPOINT = os.environ.get('AZURE_COMMUNICATION_SERVICE_ENDPOINT', '')
AZURE_EMAIL_SENDER = os.environ.get('AZURE_EMAIL_SENDER', 'noreply@netrunmail.com')
COMPANY_EMAIL = 'daniel@netrunsystems.com'
EARLY_ACCESS_EMAIL = 'earlyaccess@netrunsystems.com'

# Netrunmail service configuration
NETRUNMAIL_DOMAIN = 'netrunmail.com'
logger.info(f"Netrunmail service configured with sender: {AZURE_EMAIL_SENDER}")
logger.info(f"Communication service endpoint: {AZURE_COMMUNICATION_SERVICE_ENDPOINT[:50]}..." if AZURE_COMMUNICATION_SERVICE_ENDPOINT else "No communication service endpoint configured")

# Session config - use simple cookie-based sessions for Azure
# Flask-Session filesystem mode can cause issues in containerized environments
app.config['SESSION_TYPE'] = None  # Use default Flask sessions (cookie-based)
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

logger.info("Using cookie-based sessions for Azure compatibility")

# Enable CSRF protection
try:
    csrf = CSRFProtect(app)
    logger.info("CSRF protection enabled")
except Exception as e:
    logger.error(f"Failed to enable CSRF protection: {e}")
    csrf = None

# Create blog post directory if it doesn't exist
BLOG_POST_DIR = os.path.join(app.root_path, 'blog_posts')
try:
    os.makedirs(BLOG_POST_DIR, exist_ok=True)
    logger.info(f"Blog post directory created/verified: {BLOG_POST_DIR}")
except Exception as e:
    logger.error(f"Failed to create blog post directory: {e}")
    BLOG_POST_DIR = None

# Domain-based routing handler
@app.before_request
def handle_subdomain():
    """Handle subdomain routing for rsvp.netrunsystems.com and www redirects"""
    host = request.headers.get('Host', '').lower()
    
    # Handle RSVP subdomain
    if host == 'rsvp.netrunsystems.com':
        logger.info(f"RSVP subdomain accessed: {request.path}")
        # If accessing root of RSVP subdomain, redirect to RSVP page
        if request.path == '/':
            logger.info("Redirecting RSVP subdomain root to /rsvp")
            return redirect(url_for('rsvp'))
        # If accessing any other path on RSVP subdomain, redirect to RSVP page
        elif request.path != '/rsvp':
            logger.info(f"Redirecting RSVP subdomain path {request.path} to /rsvp")
            return redirect(url_for('rsvp'))
    
    # Handle www subdomain - redirect to main domain
    elif host == 'www.netrunsystems.com':
        logger.info(f"WWW subdomain accessed: {request.path}, redirecting to main domain")
        # Redirect www to main domain, preserving path and query string
        main_url = f"https://netrunsystems.com{request.path}"
        if request.query_string:
            main_url += f"?{request.query_string.decode()}"
        return redirect(main_url, 301)  # Permanent redirect
    
    # Handle other subdomains or domains - redirect to main site
    elif host.endswith('.netrunsystems.com') and host != 'netrunsystems.com':
        # Any other subdomain redirects to main site
        if host != 'rsvp.netrunsystems.com':  # Already handled above
            logger.info(f"Unknown subdomain {host} accessed, redirecting to main domain")
            main_url = f"https://netrunsystems.com{request.path}"
            if request.query_string:
                main_url += f"?{request.query_string.decode()}"
            return redirect(main_url, 301)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user'):
            session['state'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def _load_cache():
    if not msal:
        return None
    cache = msal.SerializableTokenCache()
    if session.get('token_cache'):
        cache.deserialize(session['token_cache'])
    return cache

def _save_cache(cache):
    if cache and hasattr(cache, 'has_state_changed') and cache.has_state_changed:
        session['token_cache'] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
    if not msal:
        logger.warning("MSAL not available, authentication will not work")
        return None
    return msal.ConfidentialClientApplication(
        AZURE_CLIENT_ID, authority=authority or AZURE_AUTHORITY,
        client_credential=AZURE_CLIENT_SECRET, token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    msal_app = _build_msal_app(authority=authority)
    if not msal_app:
        return None
    return msal_app.initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for('authorized', _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    if not cca:
        return None
    accounts = cca.get_accounts()
    if accounts:
        result = cca.acquire_token_silent(scope or [], account=accounts[0])
        _save_cache(cache)
        return result

def send_email(to_address, subject, html_content, plain_text_content=None, reply_to=None):
    """Send email using Netrunmail Azure Communication Services with Service Principal"""
    try:
        if not EmailClient or not AZURE_IDENTITY_AVAILABLE:
            logger.warning("Netrunmail Azure Communication Email or Identity not available, skipping email send")
            return False
            
        if not AZURE_COMMUNICATION_SERVICE_ENDPOINT:
            logger.warning("Netrunmail service endpoint not configured, skipping email send")
            return False
            
        if not AZURE_CLIENT_ID or not AZURE_CLIENT_SECRET or not AZURE_TENANT_ID:
            logger.warning("Service principal credentials not configured for Netrunmail")
            return False
        
        # Validate email addresses
        if not to_address or '@' not in to_address:
            logger.error(f"Invalid recipient email address: {to_address}")
            return False
            
        logger.info(f"Sending email via Netrunmail service principal from {AZURE_EMAIL_SENDER} to {to_address}")
        
        # Use DefaultAzureCredential (which will use service principal in production)
        credential = DefaultAzureCredential()
        email_client = EmailClient(endpoint=AZURE_COMMUNICATION_SERVICE_ENDPOINT, credential=credential)
        
        # Build message with optional reply-to
        message = {
            "senderAddress": AZURE_EMAIL_SENDER,
            "recipients": {
                "to": [{"address": to_address}],
            },
            "content": {
                "subject": f"[Netrun Systems] {subject}",
                "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <div style="background: #2c3e50; color: white; padding: 20px; text-align: center;">
                        <h2 style="margin: 0; color: #84baaa;">NETRUN SYSTEMS</h2>
                        <p style="margin: 5px 0 0 0; font-size: 14px;">Technology Solutions for People by People</p>
                    </div>
                    <div style="padding: 20px; background: #f8f9fa;">
                        {html_content}
                    </div>
                    <div style="background: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #666;">
                        <p>This email was sent via Netrunmail from Netrun Systems</p>
                        <p>Ojai, California | <a href="https://netrunsystems.com" style="color: #84baaa;">netrunsystems.com</a></p>
                    </div>
                </div>
                """,
                "plainText": f"NETRUN SYSTEMS\n\n{plain_text_content or html_content}\n\n---\nThis email was sent via Netrunmail from Netrun Systems\nOjai, California | netrunsystems.com"
            }
        }
        
        # Add reply-to if specified
        if reply_to and '@' in reply_to:
            message["replyTo"] = [{"address": reply_to}]
            logger.info(f"Email includes reply-to: {reply_to}")
        
        # Send email
        poller = email_client.begin_send(message)
        result = poller.result()
        
        logger.info(f"✅ Netrunmail email sent successfully to {to_address}. Message ID: {result.message_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Netrunmail email send failed to {to_address}: {str(e)}")
        return False

@app.route('/')
def index():
    now = datetime.datetime.now()
    return render_template('index.html', now=now)

@app.route('/product/intirkon')
def product_intirkon():
    now = datetime.datetime.now()
    return render_template('product_intirkon.html', now=now)

@app.route('/product/cost-optimizer')
def product_cost_optimizer():
    now = datetime.datetime.now()
    return render_template('product_cost_optimizer.html', now=now)

@app.route('/product/compliance-reporter')
def product_compliance_reporter():
    now = datetime.datetime.now()
    return render_template('product_compliance_reporter.html', now=now)

@app.route('/product/intirfix')
def product_intirfix():
    now = datetime.datetime.now()
    return render_template('product_intirfix.html', now=now)

@app.route('/product/intirkast')
def product_intirkast():
    now = datetime.datetime.now()
    return render_template('product_intirkast.html', now=now)

@app.route('/early-access', methods=['GET', 'POST'])
def early_access():
    now = datetime.datetime.now()
    if request.method == 'POST':
        email = request.form.get('email')
        
        if email:
            # Send email notification to early access team via Netrunmail
            subject = f"New Early Access Request"
            html_content = f"""
                <h2>🚀 New Early Access Program Request</h2>
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Source:</strong> Early Access Form - netrunsystems.com</p>
                </div>
                <p>Please follow up with this prospect regarding our Early Access Program.</p>
                <p style="margin-top: 20px; padding: 10px; background: #f0f8ff; border-radius: 5px;">
                    <strong>Next Steps:</strong> Send welcome email and onboarding information.
                </p>
            """
            
            if send_email(EARLY_ACCESS_EMAIL, subject, html_content, reply_to=email):
                flash('Thank you for your interest in our Early Access Program! We will contact you shortly.', 'success')
                logger.info(f"✅ Early access request processed via Netrunmail: {email}")
            else:
                flash('Thank you for your interest! We will contact you shortly.', 'success')
                logger.warning(f"❌ Netrunmail failed for early access request: {email}")
            
            return redirect(url_for('early_access'))
        else:
            flash('Please provide a valid email address.', 'error')
        
    return render_template('early_access.html', now=now)

@app.route('/blog')
def blog():
    now = datetime.datetime.now()
    posts = get_blog_posts()
    return render_template('blog.html', posts=posts, now=now)

@app.route('/blog/<slug>')
def blog_post(slug):
    now = datetime.datetime.now()
    post = get_blog_post(slug)
    if post:
        return render_template('blog_post.html', post=post, now=now)
    abort(404)

def get_blog_posts():
    posts = []
    try:
        if BLOG_POST_DIR and os.path.exists(BLOG_POST_DIR):
            for filename in os.listdir(BLOG_POST_DIR):
                if filename.endswith('.md'):
                    post = parse_blog_post(filename)
                    if post:
                        posts.append(post)
    except Exception as e:
        logger.error(f"Error getting blog posts: {str(e)}")
        return []
    
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def get_blog_post(slug):
    try:
        if BLOG_POST_DIR and os.path.exists(BLOG_POST_DIR):
            for filename in os.listdir(BLOG_POST_DIR):
                if filename.endswith('.md'):
                    post = parse_blog_post(filename)
                    if post and post['slug'] == slug:
                        return post
    except Exception as e:
        logger.error(f"Error getting blog post {slug}: {str(e)}")
    return None

def parse_blog_post(filename):
    try:
        filepath = os.path.join(BLOG_POST_DIR, filename)
        with open(filepath, 'r') as file:
            content = file.read()
        
        # Parse front matter
        front_matter_match = re.match(r'^---\s+(.*?)\s+---\s+(.*)', content, re.DOTALL)
        if not front_matter_match:
            return None
        
        front_matter = front_matter_match.group(1)
        markdown_content = front_matter_match.group(2)
        
        # Parse metadata
        metadata = {}
        for line in front_matter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        # Convert markdown to HTML
        if markdown:
            html_content = markdown.markdown(markdown_content)
        else:
            html_content = markdown_content.replace('\n', '<br>')
        
        # Create slug from title if not provided
        if 'slug' not in metadata and 'title' in metadata:
            metadata['slug'] = metadata['title'].lower().replace(' ', '-')
        
        # Parse date
        if 'date' in metadata:
            try:
                date_obj = datetime.datetime.strptime(metadata['date'], '%Y-%m-%d')
                metadata['date'] = date_obj
            except ValueError:
                metadata['date'] = datetime.datetime.now()
        else:
            metadata['date'] = datetime.datetime.now()
        
        # Format date for display
        metadata['formatted_date'] = metadata['date'].strftime('%B %d, %Y')
        
        return {
            'title': metadata.get('title', 'Untitled'),
            'author': metadata.get('author', 'Netrun Systems'),
            'date': metadata['date'],
            'formatted_date': metadata['formatted_date'],
            'slug': metadata.get('slug', ''),
            'excerpt': metadata.get('excerpt', ''),
            'image': metadata.get('image', ''),
            'content': html_content
        }
    except Exception as e:
        logger.error(f"Error parsing blog post {filename}: {str(e)}")
        return None

@app.route('/admin/login')
def admin_login():
    # Check if MSAL is available
    if not msal:
        logger.warning("MSAL not available, using development admin login")
        session['admin'] = True
        flash('Development admin login (MSAL not available)', 'warning')
        return redirect(url_for('admin_blog'))
    
    # Check if user is already authenticated
    token = _get_token_from_cache(AZURE_SCOPE)
    if not token:
        # Start the OAuth flow
        flow = _build_auth_code_flow(scopes=AZURE_SCOPE)
        if not flow:
            logger.warning("Failed to build auth flow, using development admin login")
            session['admin'] = True
            flash('Development admin login (Auth flow failed)', 'warning')
            return redirect(url_for('admin_blog'))
        
        session['flow'] = flow
        return redirect(flow['auth_uri'])
    
    # User is already authenticated
    session['admin'] = True
    return redirect(url_for('admin_blog'))

@app.route('/getAToken')
def authorized():
    try:
        if not msal:
            flash('Authentication not available (MSAL not loaded)', 'error')
            return redirect(url_for('index'))
            
        cache = _load_cache()
        msal_app = _build_msal_app(cache=cache)
        if not msal_app:
            flash('Authentication failed (MSAL app not available)', 'error')
            return redirect(url_for('index'))
            
        result = msal_app.acquire_token_by_auth_code_flow(
            session.get('flow', {}), request.args)
        if 'error' in result:
            flash(f'Authentication failed: {result.get("error_description")}', 'error')
            return redirect(url_for('index'))
        
        session['user'] = result.get('id_token_claims')
        session['admin'] = True
        _save_cache(cache)
        flash('Successfully logged in with Azure AD!', 'success')
        
    except ValueError:
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('index'))
    
    return redirect(url_for('admin_blog'))

@app.route('/admin/logout')
def admin_logout():
    session.clear()  # Clear all session data including Azure tokens
    flash('Successfully logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/admin/blog', methods=['GET', 'POST'])
@requires_admin
def admin_blog():
    now = datetime.datetime.now()
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            author = request.form.get('author')
            date_str = request.form.get('date')
            excerpt = request.form.get('excerpt')
            content = request.form.get('content')
            
            # Create slug from title
            slug = title.lower().replace(' ', '-')
            # Remove special characters
            slug = re.sub(r'[^a-z0-9-]', '', slug)
            
            # Parse date
            try:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                date = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Create markdown file
            markdown_content = f"""---
title: {title}
author: {author}
date: {date}
slug: {slug}
excerpt: {excerpt}
---
{content}
"""
            
            # Ensure blog post directory exists
            os.makedirs(BLOG_POST_DIR, exist_ok=True)
            
            filename = f"{slug}.md"
            filepath = os.path.join(BLOG_POST_DIR, filename)
            
            with open(filepath, 'w') as file:
                file.write(markdown_content)
            
            flash('Blog post created successfully!', 'success')
            return redirect(url_for('blog'))
        except Exception as e:
            app.logger.error(f"Error creating blog post: {str(e)}")
            flash(f'Error creating blog post: {str(e)}', 'error')
    
    return render_template('admin_blog.html', now=now)

@app.route('/about', methods=['GET', 'POST'])
def about():
    now = datetime.datetime.now()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if name and email and subject and message:
            # Send email notification to company via Netrunmail
            email_subject = f"Contact Form: {subject}"
            html_content = f"""
                <h2>📧 New Contact Form Submission - About Page</h2>
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>Source:</strong> About Page Contact Form</p>
                    <p><strong>Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h3>Message:</h3>
                    <p style="white-space: pre-wrap;">{message}</p>
                </div>
                <p style="margin-top: 20px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                    <strong>Action Required:</strong> Please respond to this inquiry within 24 hours.
                </p>
            """
            
            if send_email(COMPANY_EMAIL, email_subject, html_content, reply_to=email):
                flash('Thank you for your message! We will get back to you shortly.', 'success')
                logger.info(f"✅ About page contact form processed via Netrunmail: {email}")
            else:
                flash('Thank you for your message! We will get back to you shortly.', 'success')
                logger.warning(f"❌ Netrunmail failed for about page contact: {email}")
        else:
            flash('Please fill in all required fields.', 'error')
        
        return redirect(url_for('about'))
        
    return render_template('about.html', now=now)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    now = datetime.datetime.now()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if name and email and subject and message:
            # Send email notification to company via Netrunmail
            email_subject = f"Contact Form: {subject}"
            html_content = f"""
                <h2>📧 New Contact Form Submission - Main Contact Page</h2>
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <p><strong>Source:</strong> Main Contact Page Form</p>
                    <p><strong>Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h3>Message:</h3>
                    <p style="white-space: pre-wrap;">{message}</p>
                </div>
                <p style="margin-top: 20px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                    <strong>Action Required:</strong> Please respond to this inquiry within 24 hours.
                </p>
            """
            
            if send_email(COMPANY_EMAIL, email_subject, html_content, reply_to=email):
                flash('Thank you for your message! We will get back to you shortly.', 'success')
                logger.info(f"✅ Main contact form processed via Netrunmail: {email}")
            else:
                flash('Thank you for your message! We will get back to you shortly.', 'success')
                logger.warning(f"❌ Netrunmail failed for main contact form: {email}")
        else:
            flash('Please fill in all required fields.', 'error')
        
        return redirect(url_for('contact'))
        
    return render_template('contact.html', now=now)

@app.route('/health')
def health_check():
    """Health check endpoint for Azure App Service"""
    logger.info("Health check endpoint accessed")
    return {'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()}, 200

@app.route('/test-email-config')
def test_email_config():
    """Test endpoint to check email configuration and send a test email"""
    
    config_check = {
        'timestamp': datetime.datetime.now().isoformat(),
        'configuration': {
            'service_principal': {
                'client_id_set': bool(AZURE_CLIENT_ID),
                'client_secret_set': bool(AZURE_CLIENT_SECRET),
                'tenant_id_set': bool(AZURE_TENANT_ID),
                'all_set': all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID])
            },
            'communication_service': {
                'endpoint_set': bool(AZURE_COMMUNICATION_SERVICE_ENDPOINT),
                'endpoint_value': AZURE_COMMUNICATION_SERVICE_ENDPOINT[:50] + '...' if AZURE_COMMUNICATION_SERVICE_ENDPOINT else 'NOT SET',
                'sender_email': AZURE_EMAIL_SENDER,
                'company_email': COMPANY_EMAIL,
                'early_access_email': EARLY_ACCESS_EMAIL
            },
            'packages': {
                'email_client_available': EmailClient is not None,
                'azure_identity_available': AZURE_IDENTITY_AVAILABLE,
                'can_send_emails': EmailClient is not None and AZURE_IDENTITY_AVAILABLE
            },
            'legacy': {
                'connection_string_set': bool(os.environ.get('AZURE_EMAIL_CONNECTION_STRING', '')),
                'warning': 'Connection string detected - should be removed!' if os.environ.get('AZURE_EMAIL_CONNECTION_STRING') else None
            }
        },
        'diagnostics': []
    }
    
    # Run diagnostics
    if not all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID]):
        config_check['diagnostics'].append({
            'level': 'error',
            'message': 'Service principal credentials not fully configured',
            'fix': 'Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables'
        })
    
    if not AZURE_COMMUNICATION_SERVICE_ENDPOINT:
        config_check['diagnostics'].append({
            'level': 'error',
            'message': 'Communication service endpoint not configured',
            'fix': 'Set AZURE_COMMUNICATION_SERVICE_ENDPOINT environment variable'
        })
    elif not AZURE_COMMUNICATION_SERVICE_ENDPOINT.startswith('https://'):
        config_check['diagnostics'].append({
            'level': 'warning',
            'message': 'Endpoint should start with https://',
            'current': AZURE_COMMUNICATION_SERVICE_ENDPOINT
        })
    
    if os.environ.get('AZURE_EMAIL_CONNECTION_STRING'):
        config_check['diagnostics'].append({
            'level': 'warning',
            'message': 'Old connection string still present',
            'fix': 'Remove AZURE_EMAIL_CONNECTION_STRING and use service principal authentication'
        })
    
    if not EmailClient or not AZURE_IDENTITY_AVAILABLE:
        config_check['diagnostics'].append({
            'level': 'error',
            'message': 'Required packages not available',
            'fix': 'Install azure-communication-email and azure-identity packages'
        })
    
    # Test email sending if requested
    if request.args.get('send_test') == 'true':
        test_email = request.args.get('email', COMPANY_EMAIL)
        config_check['email_test'] = {
            'recipient': test_email,
            'attempting': True
        }
        
        try:
            html_content = f"""
                <h2>🧪 Email Configuration Test</h2>
                <p>This is a test email from the Netrunmail service.</p>
                <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3>Configuration Details:</h3>
                    <ul>
                        <li><strong>Sender:</strong> {AZURE_EMAIL_SENDER}</li>
                        <li><strong>Endpoint:</strong> {AZURE_COMMUNICATION_SERVICE_ENDPOINT[:50]}...</li>
                        <li><strong>Time:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                        <li><strong>Service Principal:</strong> {'✅ Configured' if all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID]) else '❌ Not configured'}</li>
                    </ul>
                </div>
                <p>If you received this email, the email service is working correctly!</p>
            """
            
            success = send_email(
                to_address=test_email,
                subject="Email Configuration Test",
                html_content=html_content,
                plain_text_content="This is a test email from Netrunmail. Configuration test successful!"
            )
            
            config_check['email_test']['success'] = success
            config_check['email_test']['message'] = 'Email sent successfully!' if success else 'Email send failed - check logs'
            
        except Exception as e:
            config_check['email_test']['success'] = False
            config_check['email_test']['error'] = str(e)
            logger.error(f"Test email failed: {e}")
    
    # Add recommendations
    config_check['recommendations'] = []
    
    if len(config_check['diagnostics']) == 0:
        config_check['status'] = 'ready'
        config_check['recommendations'].append('Configuration looks good! Try sending a test email with ?send_test=true&email=your@email.com')
    else:
        config_check['status'] = 'issues_found'
        config_check['recommendations'].append('Fix the issues listed in diagnostics before testing email sending')
    
    return config_check, 200

@app.route('/debug')
def debug_info():
    """Debug endpoint to check application status"""
    return {
        'status': 'running',
        'timestamp': datetime.datetime.now().isoformat(),
        'dependencies': {
            'markdown': markdown is not None,
            'msal': msal is not None,
            'requests': requests is not None,
            'netrunmail_client': EmailClient is not None,
        },
        'config': {
            'blog_dir_exists': BLOG_POST_DIR is not None and os.path.exists(BLOG_POST_DIR) if BLOG_POST_DIR else False,
            'dev_mode': DEV_MODE,
            'azure_service_principal': bool(AZURE_CLIENT_ID and AZURE_CLIENT_SECRET and AZURE_TENANT_ID),
            'netrunmail_service_endpoint': bool(AZURE_COMMUNICATION_SERVICE_ENDPOINT),
            'netrunmail_sender': AZURE_EMAIL_SENDER,
            'netrunmail_domain': NETRUNMAIL_DOMAIN,
            'azure_identity_available': AZURE_IDENTITY_AVAILABLE,
        },
        'packages': {
            'flask': '2.3.3',
            'minimal_deployment': True,
            'advanced_azure_services': False
        }
    }, 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def create_sample_content():
    try:
        # Ensure blog post directory exists
        if not BLOG_POST_DIR:
            logger.warning("Blog post directory not available, skipping sample content creation")
            return
            
        os.makedirs(BLOG_POST_DIR, exist_ok=True)
        
        # Check if any blog posts exist
        if not os.listdir(BLOG_POST_DIR):
            # Create a sample blog post
            sample_post = """---
title: Welcome to Netrun Systems
author: Netrun Systems
date: 2025-04-24
slug: welcome-to-netrun-systems
excerpt: Welcome to the Netrun Systems blog where we'll share insights on Azure cross-tenant governance and cloud management.
---
# Welcome to Netrun Systems

Thank you for visiting the Netrun Systems blog. Here we'll share insights, best practices, and updates about our cross-tenant governance solutions for Azure.

## Our Mission

At Netrun Systems, we're dedicated to helping Azure consultants and MSPs manage multiple client environments securely and efficiently. Our flagship product, Netrun Systems Nexus, leverages Azure Lighthouse technology to provide secure cross-tenant access management without sharing credentials or adding guest accounts.

## Stay Tuned

Check back regularly for:
- Technical deep dives
- Best practices for Azure governance
- Product updates and new features
- Case studies and success stories

We're excited to have you join us on this journey!
"""
            with open(os.path.join(BLOG_POST_DIR, 'welcome-to-netrun-systems.md'), 'w') as f:
                f.write(sample_post)
    except Exception as e:
        logger.error(f"Error creating sample content: {str(e)}")

# Call create_sample_content when the app starts
try:
    create_sample_content()
    logger.info("Sample content creation completed")
except Exception as e:
    logger.error(f"Failed to create sample content: {e}")

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/services')
def services():
    now = datetime.datetime.now()
    return render_template('services.html', now=now)

@app.route('/product/small-business-optimization-suite')
def product_small_business_optimization_suite():
    now = datetime.datetime.now()
    return render_template('product_small_business_optimization_suite.html', now=now)

@app.route('/research-projects')
def research_projects():
    now = datetime.datetime.now()
    return render_template('research_projects.html', now=now)

@app.route('/research/sunflower')
def research_sunflower():
    now = datetime.datetime.now()
    return render_template('research_sunflower.html', now=now)

@app.route('/research/podcast-cohost')
def research_podcast_cohost():
    now = datetime.datetime.now()
    return render_template('research_podcast_cohost.html', now=now)

@app.route('/research/scrum-master')
def research_scrum_master():
    now = datetime.datetime.now()
    return render_template('research_scrum_master.html', now=now)

@app.route('/research/connection-manager')
def research_connection_manager():
    now = datetime.datetime.now()
    return render_template('research_connection_manager.html', now=now)

@app.route('/rsvp', methods=['GET', 'POST'])
def rsvp():
    now = datetime.datetime.now()
    if request.method == 'POST':
        business_name = request.form.get('business_name')
        attendee_name = request.form.get('attendee_name')
        plus_one = request.form.get('plus_one') == 'yes'
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        text_communication = request.form.get('text_communication') == 'yes'
        response = request.form.get('response')  # 'accept' or 'decline'
        
        if business_name and attendee_name and email and response:
            # Send email notification to events team via Netrunmail
            status = "ACCEPTED" if response == 'accept' else "DECLINED"
            status_emoji = "✅" if response == 'accept' else "❌"
            plus_one_text = "Yes" if plus_one else "No"
            text_consent = "Yes" if text_communication else "No"
            
            subject = f"Neural Networking Event RSVP {status}: {attendee_name}"
            html_content = f"""
                <h2>{status_emoji} Neural Networking Event RSVP - {status}</h2>
                <div style="background: {'#e8f5e8' if response == 'accept' else '#ffebee'}; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <h3>Attendee Information</h3>
                    <p><strong>Business Name:</strong> {business_name}</p>
                    <p><strong>Attendee Name:</strong> {attendee_name}</p>
                    <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                    <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
                    <p><strong>Plus One:</strong> {plus_one_text}</p>
                    <p><strong>Text Communication Consent:</strong> {text_consent}</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <p><strong>Response:</strong> <span style="color: {'green' if response == 'accept' else 'red'}; font-weight: bold;">{status}</span></p>
                    <p><strong>Event:</strong> Neural Networking: The Future of AI-Driven Business Solutions</p>
                    <p><strong>Date:</strong> March 15, 2025 | 6:00 PM - 9:00 PM PST</p>
                    <p><strong>Location:</strong> Ojai Valley, California</p>
                    <p><strong>Submission Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <p style="margin-top: 20px; padding: 10px; background: {'#d4edda' if response == 'accept' else '#f8d7da'}; border-radius: 5px;">
                    <strong>Next Steps:</strong> {'Send event details and confirmation email to attendee.' if response == 'accept' else 'Update guest list and send follow-up for future events.'}
                </p>
            """
            
            if send_email(COMPANY_EMAIL, subject, html_content, reply_to=email):
                if response == 'accept':
                    flash('Thank you for your RSVP! We look forward to seeing you at the event.', 'success')
                    logger.info(f"✅ RSVP ACCEPTED processed via Netrunmail: {attendee_name} ({email})")
                else:
                    flash('Thank you for letting us know. We hope to see you at a future event.', 'success')
                    logger.info(f"✅ RSVP DECLINED processed via Netrunmail: {attendee_name} ({email})")
            else:
                if response == 'accept':
                    flash('Thank you for your RSVP! We look forward to seeing you at the event.', 'success')
                else:
                    flash('Thank you for letting us know. We hope to see you at a future event.', 'success')
                logger.warning(f"❌ Netrunmail failed for RSVP {status}: {attendee_name} ({email})")
            
            return redirect(url_for('rsvp'))
        else:
            flash('Please fill in all required fields.', 'error')
        
    return render_template('rsvp.html', now=now)



@app.route('/login')
def login():
    # In development mode, automatically log in
    session['user'] = {
        'name': 'Development User',
        'email': 'dev@netrunsystems.com',
        'id': 'dev-user-id'
    }
    return redirect(url_for('customer_portal'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/portal')
@requires_auth
def customer_portal():
    user = session.get('user')
    return render_template('customer_portal.html',
                         user=user,
                         version="2.0.0")  # Hardcoded version for development

@app.route('/portal/profile')
@requires_auth
def customer_profile():
    user = session.get('user')
    return render_template('customer_profile.html', user=user)

@app.route('/portal/resources')
@requires_auth
def customer_resources():
    user = session.get('user')
    return render_template('customer_resources.html', user=user)

@app.route('/portal/support')
@requires_auth
def customer_support():
    user = session.get('user')
    return render_template('customer_support.html', user=user)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    now = datetime.datetime.now()
    return render_template('404.html', now=now), 404

@app.errorhandler(500)
def internal_error(e):
    now = datetime.datetime.now()
    return render_template('500.html', now=now), 500

@app.route('/product/governance-dashboard')
def product_governance_dashboard():
    now = datetime.datetime.now()
    return render_template('product_governance_dashboard.html', now=now)

# This is required for Azure App Service to find the application
application = app

logger.info("Flask application initialization completed successfully")

# Log application startup for Azure diagnostics
# Note: before_first_request is deprecated in Flask 2.3+
def log_startup():
    port = os.environ.get('PORT', 'not set')
    logger.info(f"Application starting up - PORT environment variable: {port}")
    logger.info(f"Application available at /health endpoint")
    logger.info(f"Application available at /debug endpoint")

# Call it immediately on startup
log_startup()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    logger.info(f"Starting Flask application on host=0.0.0.0, port={port}, debug={debug_mode}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
