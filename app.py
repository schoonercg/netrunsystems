
import os
import re
import datetime
import markdown
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
from functools import wraps
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add CSRF token to template context
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_blog_posts():
    """Get blog posts from the local blog_posts directory."""
    posts = []
    blog_dir = os.path.join(os.path.dirname(__file__), 'blog_posts')
    
    if not os.path.exists(blog_dir):
        return posts
    
    for filename in os.listdir(blog_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(blog_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    post = parse_blog_post(content, filename)
                    if post:
                        posts.append(post)
            except Exception as e:
                app.logger.error(f"Error reading blog post {filename}: {str(e)}")
    
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def get_blog_post(slug):
    """Get a specific blog post by slug."""
    posts = get_blog_posts()
    for post in posts:
        if post['slug'] == slug:
            return post
    return None

def parse_blog_post(content, filename):
    """Parse blog post content and metadata."""
    try:
        # Parse front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                front_matter = parts[1].strip()
                markdown_content = parts[2].strip()
            else:
                front_matter = ''
                markdown_content = content
        else:
            front_matter = ''
            markdown_content = content
        
        # Parse metadata
        metadata = {}
        for line in front_matter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Create slug from filename if not provided
        if 'slug' not in metadata:
            metadata['slug'] = filename.replace('.md', '').replace('_', '-')
        
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
        app.logger.error(f"Error parsing blog post: {str(e)}")
        return None

def send_early_access_email(name, company, email, phone, message):
    """Send email notification for early access requests"""
    
    # Email configuration - using environment variables for security
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_username = os.environ.get('SMTP_USERNAME', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    
    # If no SMTP credentials are configured, log the request instead
    if not smtp_username or not smtp_password:
        app.logger.info(f"Early Access Request - Name: {name}, Company: {company}, Email: {email}, Phone: {phone}, Message: {message}")
        return
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = 'daniel@netrunsystems.com'
    msg['Subject'] = f'Early Access Request from {name} at {company}'
    
    # Email body
    body = f"""
New Early Access Request

Name: {name}
Company: {company}
Email: {email}
Phone: {phone or "Not provided"}

Message:
{message}

Submitted at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, 'daniel@netrunsystems.com', text)
        server.quit()
        app.logger.info(f"Early access email sent successfully for {name}")
    except Exception as e:
        app.logger.error(f"Failed to send early access email: {str(e)}")
        raise

def send_contact_notification(name, email, subject, message):
    """Send email notification for contact form submissions"""
    
    # Email configuration - using environment variables for security
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_username = os.environ.get('SMTP_USERNAME', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    
    # If no SMTP credentials are configured, log the request instead
    if not smtp_username or not smtp_password:
        app.logger.info(f"Contact Form - Name: {name}, Email: {email}, Subject: {subject}, Message: {message}")
        return
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = 'daniel@netrunsystems.com'
    msg['Subject'] = f'Contact Form: {subject or "General Inquiry"} from {name}'
    
    # Email body
    body = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Subject: {subject or "No subject provided"}

Message:
{message}

Submitted at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, 'daniel@netrunsystems.com', text)
        server.quit()
        app.logger.info(f"Contact email sent successfully for {name}")
    except Exception as e:
        app.logger.error(f"Failed to send contact email: {str(e)}")
        raise

def create_sample_content():
    try:
        # Ensure blog post directory exists
        blog_dir = os.path.join(os.path.dirname(__file__), 'blog_posts')
        os.makedirs(blog_dir, exist_ok=True)
        
        # Create welcome blog post if it doesn't exist
        welcome_post_path = os.path.join(blog_dir, 'welcome-to-netrun-systems.md')
        if not os.path.exists(welcome_post_path):
            welcome_content = """---
title: Welcome to Netrun Systems
author: Daniel Garza
date: 2024-01-15
excerpt: Introducing Netrun Systems and our mission to revolutionize Azure management for businesses.
image: /static/images/ns-banner.png
slug: welcome-to-netrun-systems
---

# Welcome to Netrun Systems

We're excited to introduce Netrun Systems, your partner in Azure cloud management and optimization. Our team is dedicated to helping businesses maximize their cloud investments through innovative solutions and expert guidance.

## Our Mission

At Netrun Systems, we believe that cloud technology should empower businesses, not complicate them. Our suite of Azure management tools is designed to simplify operations, enhance security, and optimize costs.

## What We Offer

- **Intirkon Cloud Management Suite**: Comprehensive Azure management platform
- **Intirfix Business Intelligence**: Smart analytics for better decision making
- **Intirkast Content Management**: Streamlined content operations
- **Expert Consulting Services**: Personalized guidance for your Azure journey

Stay tuned for more updates as we continue to innovate and expand our offerings.
"""
            with open(welcome_post_path, 'w') as f:
                f.write(welcome_content)
            app.logger.info("Created welcome blog post")
        
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

@app.route('/')
def index():
    now = datetime.datetime.now()
    return render_template('index.html', now=now)

@app.route('/about', methods=['GET', 'POST'])
def about():
    now = datetime.datetime.now()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Send email notification
        try:
            send_contact_notification(name, email, subject, message)
            flash('Thank you for your message! We will get back to you shortly.', 'success')
        except Exception as e:
            app.logger.error(f"Error sending contact email: {str(e)}")
            flash('Thank you for your message! We have received your inquiry and will get back to you shortly.', 'success')
        
        return redirect(url_for('about'))
        
    return render_template('about.html', now=now)

@app.route('/ojai-tech-center')
def ojai_tech_center():
    now = datetime.datetime.now()
    return render_template('ojai_tech_center.html', now=now)

@app.route('/services')
def services():
    now = datetime.datetime.now()
    return render_template('services.html', now=now)

@app.route('/solutions')
def solutions():
    now = datetime.datetime.now()
    return render_template('solutions.html', now=now)

@app.route('/product/intirkon')
def product_intirkon():
    now = datetime.datetime.now()
    return render_template('product_intirkon.html', now=now)

@app.route('/product/intirfix')
def product_intirfix():
    now = datetime.datetime.now()
    return render_template('product_intirfix.html', now=now)

@app.route('/product/intirkast')
def product_intirkast():
    now = datetime.datetime.now()
    return render_template('product_intirkast.html', now=now)

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
        
        # Send email notification
        try:
            send_early_access_email(name, company, email, phone, message)
            flash('Thank you for your interest in our Early Access Program! We will contact you shortly.', 'success')
        except Exception as e:
            app.logger.error(f"Error sending early access email: {str(e)}")
            flash('Thank you for your interest in our Early Access Program! We have received your request and will contact you shortly.', 'success')
        
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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    now = datetime.datetime.now()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Send email notification
        try:
            send_contact_notification(name, email, subject, message)
            flash('Thank you for your message! We will get back to you shortly.', 'success')
        except Exception as e:
            app.logger.error(f"Error sending contact email: {str(e)}")
            flash('Thank you for your message! We have received your inquiry and will get back to you shortly.', 'success')
        
        return redirect(url_for('contact'))
        
    return render_template('contact.html', now=now)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def page_not_found(e):
    now = datetime.datetime.now()
    return render_template('404.html', now=now), 404

@app.errorhandler(500)
def internal_server_error(e):
    now = datetime.datetime.now()
    return render_template('500.html', now=now), 500

# This is required for Azure App Service to find the application
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
