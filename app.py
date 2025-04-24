import os
import markdown
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create Flask application instance
# This variable name 'app' is critical for Azure App Service deployment
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Blog configuration
BLOG_POST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog_posts')
if not os.path.exists(BLOG_POST_DIR):
    os.makedirs(BLOG_POST_DIR)

# Ensure static directories exist
for dir_path in ['static/images', 'static/css', 'static/js']:
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

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
        email = request.form.get('email')
        company = request.form.get('company')
        role = request.form.get('role')
        tenants = request.form.get('tenants')
        message = request.form.get('message')
        
        # Send email to NSXearlyaccess@netrunsystems.com
        try:
            send_early_access_email(name, email, company, role, tenants, message)
            flash('Thank you for your interest in our Early Access Program! We will contact you shortly.', 'success')
        except Exception as e:
            flash(f'There was an error submitting your application. Please try again later.', 'error')
            print(f"Email error: {str(e)}")
            
        return redirect(url_for('early_access'))
        
    return render_template('early_access.html', now=now)

def send_early_access_email(name, email, company, role, tenants, message):
    # In a production environment, this would use SMTP to send an actual email
    # For now, we'll just print the email content to the console
    print(f"Early Access Application from {name} ({email})")
    print(f"Company: {company}")
    print(f"Role: {role}")
    print(f"Number of Azure Tenants: {tenants}")
    print(f"Message: {message}")
    
    # In production, uncomment and configure this code:
    """
    msg = MIMEMultipart()
    msg['From'] = 'website@netrunsystems.com'
    msg['To'] = 'NSXearlyaccess@netrunsystems.com'
    msg['Subject'] = f'Early Access Application: {company}'
    
    body = f'''
    Name: {name}
    Email: {email}
    Company: {company}
    Role: {role}
    Number of Azure Tenants: {tenants}
    
    Message:
    {message}
    '''
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP('smtp.yourserver.com', 587)
    server.starttls()
    server.login('your_email@example.com', 'your_password')
    text = msg.as_string()
    server.sendmail('website@netrunsystems.com', 'NSXearlyaccess@netrunsystems.com', text)
    server.quit()
    """

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
    if os.path.exists(BLOG_POST_DIR):
        for filename in os.listdir(BLOG_POST_DIR):
            if filename.endswith('.md'):
                post = parse_blog_post(filename)
                if post:
                    posts.append(post)
    
    # Sort posts by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def get_blog_post(slug):
    if os.path.exists(BLOG_POST_DIR):
        for filename in os.listdir(BLOG_POST_DIR):
            if filename.endswith('.md'):
                post = parse_blog_post(filename)
                if post and post['slug'] == slug:
                    return post
    return None

def parse_blog_post(filename):
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
    html_content = markdown.markdown(markdown_content, extensions=['extra'])
    
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

@app.route('/admin/blog', methods=['GET', 'POST'])
def admin_blog():
    now = datetime.datetime.now()
    if request.method == 'POST':
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
        
        filename = f"{slug}.md"
        filepath = os.path.join(BLOG_POST_DIR, filename)
        
        with open(filepath, 'w') as file:
            file.write(markdown_content)
        
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('blog'))
    
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

# This is required for Azure App Service to find the application
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)
