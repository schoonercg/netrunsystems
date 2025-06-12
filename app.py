import os
import re
import datetime
import markdown
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, session
from flask_wtf import CSRFProtect
from flask_session import Session
from functools import wraps
from config import get_config
from security import init_security, require_azure_ad, validate_input, sanitize_html, log_security_event
from azure_utils import azure_manager
import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Azure Key Vault client using managed identity
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url="https://netrun-keyvault.vault.azure.net/", credential=credential)

# Load secrets from Key Vault
AZURE_AD_CLIENT_ID = secret_client.get_secret("AZURE-AD-CLIENT-ID").value
AZURE_AD_CLIENT_SECRET = secret_client.get_secret("AZURE-AD-CLIENT-SECRET").value
AZURE_AD_TENANT_ID = secret_client.get_secret("AZURE-AD-TENANT-ID").value
MAIL_USERNAME = secret_client.get_secret("EMAIL-USER").value
MAIL_PASSWORD = secret_client.get_secret("EMAIL-PASSWORD").value

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(get_config())
    
    # Initialize extensions
    csrf = CSRFProtect(app)
    Session(app)
    
    # Initialize security features
    limiter = init_security(app)
    
    # Initialize Azure services
    azure_manager.init_app(app)
    
    # Create blog post directory if it doesn't exist
    os.makedirs(app.config['BLOG_POST_DIR'], exist_ok=True)
    
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        log_security_event('page_not_found', request.path)
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        log_security_event('internal_error', str(e))
        return render_template('500.html'), 500
    
    # Register routes
    register_routes(app, limiter)
    
    return app

def register_routes(app, limiter):
    """Register application routes."""
    
    @app.route('/')
    def index():
        return render_template('index.html', now=datetime.datetime.now())
    
    @app.route('/login')
    def login():
        if session.get('user'):
            return redirect(url_for('customer_portal'))
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
    
    @app.route('/portal')
    @require_azure_ad
    def customer_portal():
        return render_template('portal.html')
    
    @app.route('/blog')
    @limiter.limit("30 per minute")
    def blog():
        posts = get_blog_posts()
        return render_template('blog.html', posts=posts)
    
    @app.route('/blog/<slug>')
    @limiter.limit("30 per minute")
    def blog_post(slug):
        post = get_blog_post(slug)
        if post:
            return render_template('blog_post.html', post=post)
        abort(404)
    
    @app.route('/contact', methods=['GET', 'POST'])
    @limiter.limit("5 per minute")
    def contact():
        if request.method == 'POST':
            # Validate input
            rules = {
                'name': lambda x: len(x) > 0 and len(x) <= 100,
                'email': lambda x: re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', x),
                'message': lambda x: len(x) > 0 and len(x) <= 1000
            }
            
            if not validate_input(request.form, rules):
                flash('Invalid input. Please check your form data.', 'error')
                return redirect(url_for('contact'))
            
            # Process contact form
            try:
                # Store in Azure Blob Storage
                contact_data = {
                    'name': request.form['name'],
                    'email': request.form['email'],
                    'message': request.form['message'],
                    'timestamp': datetime.datetime.utcnow().isoformat()
                }
                azure_manager.upload_blob(
                    'contacts',
                    f"contact_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                    str(contact_data)
                )
                flash('Thank you for your message. We will get back to you soon.', 'success')
            except Exception as e:
                logger.error(f"Failed to process contact form: {str(e)}")
                flash('An error occurred. Please try again later.', 'error')
            
            return redirect(url_for('contact'))
        
        return render_template('contact.html')

def get_blog_posts():
    """Retrieve blog posts from Azure Blob Storage."""
    try:
        posts = []
        container_client = azure_manager.blob_service_client.get_container_client('blog-posts')
        for blob in container_client.list_blobs():
            if blob.name.endswith('.md'):
                content = azure_manager.download_blob('blog-posts', blob.name)
                post = parse_blog_post(content.decode('utf-8'))
                if post:
                    posts.append(post)
        
        # Sort posts by date (newest first)
        posts.sort(key=lambda x: x['date'], reverse=True)
        return posts
    except Exception as e:
        logger.error(f"Error getting blog posts: {str(e)}")
        return []

def parse_blog_post(content):
    """Parse blog post content and metadata."""
    try:
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
        
        # Convert markdown to HTML and sanitize
        html_content = sanitize_html(markdown.markdown(markdown_content))
        
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
        
        return {
            'title': metadata.get('title', 'Untitled'),
            'author': metadata.get('author', 'Netrun Systems'),
            'date': metadata['date'],
            'formatted_date': metadata['date'].strftime('%B %d, %Y'),
            'slug': metadata.get('slug', ''),
            'excerpt': metadata.get('excerpt', ''),
            'image': metadata.get('image', ''),
            'content': html_content
        }
    except Exception as e:
        logger.error(f"Error parsing blog post: {str(e)}")
        return None

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run()
