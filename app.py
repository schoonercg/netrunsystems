
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
    from flask_session import Session
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
    logger.info("Azure Communication Email import successful")
except ImportError:
    logger.warning("Azure Communication Email not available, email functionality will be disabled")
    EmailClient = None

# Development mode flag
DEV_MODE = True  # Force development mode for local testing

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

# Azure Email Configuration
AZURE_EMAIL_CONNECTION_STRING = os.environ.get('AZURE_EMAIL_CONNECTION_STRING', '')
AZURE_EMAIL_SENDER = os.environ.get('AZURE_EMAIL_SENDER', 'DoNotReply@netrunsystems.com')
COMPANY_EMAIL = 'daniel@netrunsystems.com'
EARLY_ACCESS_EMAIL = 'NSXearlyaccess@netrunsystems.com'

# Session config
app.config['SESSION_TYPE'] = 'filesystem'
try:
    Session(app)
    logger.info("Session configuration successful")
except Exception as e:
    logger.error(f"Failed to configure session: {e}")

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

def send_email(to_address, subject, html_content, plain_text_content=None):
    """Send email using Azure Communication Services"""
    try:
        if not EmailClient:
            logger.warning("Azure Communication Email not available, skipping email send")
            return False
            
        if not AZURE_EMAIL_CONNECTION_STRING:
            logger.warning("Azure Email connection string not configured, skipping email send")
            return False
            
        email_client = EmailClient.from_connection_string(AZURE_EMAIL_CONNECTION_STRING)
        
        message = {
            "senderAddress": AZURE_EMAIL_SENDER,
            "recipients": {
                "to": [{"address": to_address}],
            },
            "content": {
                "subject": subject,
                "html": html_content,
                "plainText": plain_text_content or html_content
            }
        }
        
        poller = email_client.begin_send(message)
        result = poller.result()
        
        app.logger.info(f"Email sent successfully. Message ID: {result.message_id}")
        return True
        
    except Exception as e:
        app.logger.error(f"Error sending email: {str(e)}")
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
            # Send email notification to early access team
            subject = f"New Early Access Request from {email}"
            html_content = f"""
            <html>
            <body>
                <h2>New Early Access Program Request</h2>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Please follow up with this prospect regarding our Early Access Program.</p>
            </body>
            </html>
            """
            
            if send_email(EARLY_ACCESS_EMAIL, subject, html_content):
                flash('Thank you for your interest in our Early Access Program! We will contact you shortly.', 'success')
            else:
                flash('Thank you for your interest! We will contact you shortly.', 'success')
                app.logger.warning(f"Email failed to send for early access request: {email}")
            
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
            # Send email notification to company
            email_subject = f"Contact Form: {subject}"
            html_content = f"""
            <html>
            <body>
                <h2>New Contact Form Submission</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Message:</strong></p>
                <p>{message.replace(chr(10), '<br>')}</p>
                <p><strong>Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            
            if send_email(COMPANY_EMAIL, email_subject, html_content):
                flash('Thank you for your message! We will get back to you shortly.', 'success')
            else:
                flash('Thank you for your message! We will get back to you shortly.', 'success')
                app.logger.warning(f"Email failed to send for contact form: {email}")
        else:
            flash('Please fill in all required fields.', 'error')
        
        return redirect(url_for('about'))
        
    return render_template('about.html', now=now)

@app.route('/health')
def health_check():
    """Health check endpoint for Azure App Service"""
    return {'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()}, 200

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
            'email_client': EmailClient is not None,
        },
        'config': {
            'blog_dir_exists': BLOG_POST_DIR is not None and os.path.exists(BLOG_POST_DIR) if BLOG_POST_DIR else False,
            'dev_mode': DEV_MODE,
            'azure_config': bool(AZURE_CLIENT_ID and AZURE_CLIENT_SECRET),
            'email_config': bool(AZURE_EMAIL_CONNECTION_STRING),
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
            # Send email notification to events team
            status = "ACCEPTED" if response == 'accept' else "DECLINED"
            plus_one_text = "Yes" if plus_one else "No"
            text_consent = "Yes" if text_communication else "No"
            
            subject = f"Event RSVP {status}: {attendee_name} from {business_name}"
            html_content = f"""
            <html>
            <body>
                <h2>Event RSVP Submission - {status}</h2>
                <p><strong>Business Name:</strong> {business_name}</p>
                <p><strong>Attendee Name:</strong> {attendee_name}</p>
                <p><strong>Plus One:</strong> {plus_one_text}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
                <p><strong>Text Communication Consent:</strong> {text_consent}</p>
                <p><strong>Response:</strong> {status}</p>
                <p><strong>Date:</strong> {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            
            if send_email(COMPANY_EMAIL, subject, html_content):
                if response == 'accept':
                    flash('Thank you for your RSVP! We look forward to seeing you at the event.', 'success')
                else:
                    flash('Thank you for letting us know. We hope to see you at a future event.', 'success')
            else:
                if response == 'accept':
                    flash('Thank you for your RSVP! We look forward to seeing you at the event.', 'success')
                else:
                    flash('Thank you for letting us know. We hope to see you at a future event.', 'success')
                app.logger.warning(f"Email failed to send for RSVP: {email}")
            
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting Flask development server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
