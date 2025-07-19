import os
import re
import datetime
import markdown
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, session
from flask_wtf import CSRFProtect
from flask_session import Session
from functools import wraps

# Development mode flag
DEV_MODE = True  # Force development mode for local testing

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'netrun-development-key')

# Session config
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Enable CSRF protection
csrf = CSRFProtect(app)

# Create blog post directory if it doesn't exist
BLOG_POST_DIR = os.path.join(app.root_path, 'blog_posts')
os.makedirs(BLOG_POST_DIR, exist_ok=True)

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user'):
            session['state'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    now = datetime.datetime.now()
    return render_template('index.html', now=now)

@app.route('/product/nexus-core')
def product_nexus_core():
    now = datetime.datetime.now()
    return render_template('product_nexus_core.html', now=now)

@app.route('/product/cost-optimizer')
def product_cost_optimizer():
    now = datetime.datetime.now()
    return render_template('product_cost_optimizer.html', now=now)

@app.route('/product/compliance-reporter')
def product_compliance_reporter():
    now = datetime.datetime.now()
    return render_template('product_compliance_reporter.html', now=now)

@app.route('/product/governance-dashboard')
def product_governance_dashboard():
    now = datetime.datetime.now()
    return render_template('product_governance_dashboard.html', now=now)

@app.route('/early-access', methods=['GET', 'POST'])
def early_access():
    now = datetime.datetime.now()
    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # In a production environment, this would send an email to NSXearlyaccess@netrunsystems.com
        # For now, just show a success message
        flash('Thank you for your interest in our Early Access Program! We will contact you shortly.', 'success')
        return redirect(url_for('early_access'))
        
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
        if os.path.exists(BLOG_POST_DIR):
            for filename in os.listdir(BLOG_POST_DIR):
                if filename.endswith('.md'):
                    post = parse_blog_post(filename)
                    if post:
                        posts.append(post)
    except Exception as e:
        app.logger.error(f"Error getting blog posts: {str(e)}")
        return []
    
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def get_blog_post(slug):
    try:
        if os.path.exists(BLOG_POST_DIR):
            for filename in os.listdir(BLOG_POST_DIR):
                if filename.endswith('.md'):
                    post = parse_blog_post(filename)
                    if post and post['slug'] == slug:
                        return post
    except Exception as e:
        app.logger.error(f"Error getting blog post {slug}: {str(e)}")
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
        html_content = markdown.markdown(markdown_content)
        
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
        app.logger.error(f"Error parsing blog post {filename}: {str(e)}")
        return None

@app.route('/admin/blog', methods=['GET', 'POST'])
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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    now = datetime.datetime.now()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # In a production environment, this would send an email
        # For now, just show a success message
        flash('Thank you for your message! We will get back to you shortly.', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html', now=now)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def create_sample_content():
    try:
        # Ensure blog post directory exists
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
        app.logger.error(f"Error creating sample content: {str(e)}")

# Call create_sample_content when the app starts
create_sample_content()

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/consulting')
def consulting_services():
    now = datetime.datetime.now()
    return render_template('consulting_services.html', now=now)

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

# This is required for Azure App Service to find the application
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)
