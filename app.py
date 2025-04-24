import os
import re
import sys
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create Flask app
app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.secret_key = os.environ.get('SECRET_KEY', 'netrun-development-key')

# Simplified blog functionality that doesn't rely on file system operations
def get_sample_blog_posts():
    """Return hardcoded sample blog posts instead of reading from files"""
    return [
        {
            'title': 'Welcome to Netrun Systems',
            'author': 'Netrun Systems',
            'date': datetime.datetime.now(),
            'formatted_date': datetime.datetime.now().strftime('%B %d, %Y'),
            'slug': 'welcome-to-netrun-systems',
            'excerpt': 'Welcome to the Netrun Systems blog where we\'ll share insights on Azure cross-tenant governance and cloud management.',
            'content': """
            <h1>Welcome to Netrun Systems</h1>
            <p>Thank you for visiting the Netrun Systems blog. Here we'll share insights, best practices, and updates about our cross-tenant governance solutions for Azure.</p>
            <h2>Our Mission</h2>
            <p>At Netrun Systems, we're dedicated to helping Azure consultants and MSPs manage multiple client environments securely and efficiently. Our flagship product, Netrun Systems Nexus, leverages Azure Lighthouse technology to provide secure cross-tenant access management without sharing credentials or adding guest accounts.</p>
            <h2>Stay Tuned</h2>
            <p>Check back regularly for:</p>
            <ul>
            <li>Technical deep dives</li>
            <li>Best practices for Azure governance</li>
            <li>Product updates and new features</li>
            <li>Case studies and success stories</li>
            </ul>
            <p>We're excited to have you join us on this journey!</p>
            """
        },
        {
            'title': 'Cross-Tenant Governance in Azure',
            'author': 'Netrun Systems',
            'date': datetime.datetime.now() - datetime.timedelta(days=7),
            'formatted_date': (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%B %d, %Y'),
            'slug': 'cross-tenant-governance-azure',
            'excerpt': 'Learn about the challenges and solutions for managing multiple Azure tenants securely and efficiently.',
            'content': """
            <h1>Cross-Tenant Governance in Azure</h1>
            <p>Managing multiple Azure tenants presents unique challenges for consultants and MSPs. This article explores best practices for cross-tenant governance.</p>
            <h2>Common Challenges</h2>
            <p>Azure consultants often face several challenges when managing multiple client environments:</p>
            <ul>
            <li>Security and access management</li>
            <li>Consistent policy enforcement</li>
            <li>Cost optimization across tenants</li>
            <li>Compliance reporting and auditing</li>
            </ul>
            <h2>Azure Lighthouse</h2>
            <p>Microsoft's Azure Lighthouse provides a foundation for cross-tenant management, but many organizations need additional tools and processes to fully address their governance needs.</p>
            <h2>Netrun Systems Approach</h2>
            <p>Our solutions build on Azure Lighthouse to provide comprehensive cross-tenant governance with enhanced security, reporting, and automation capabilities.</p>
            """
        }
    ]

def get_sample_blog_post(slug):
    """Return a specific sample blog post by slug"""
    posts = get_sample_blog_posts()
    for post in posts:
        if post['slug'] == slug:
            return post
    return None

@app.route('/')
def index():
    try:
        now = datetime.datetime.now()
        app.logger.info("Rendering index page")
        return render_template('index.html', now=now)
    except Exception as e:
        app.logger.error(f"Error rendering index page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/health')
def health():
    """Simple health check endpoint that doesn't rely on file system operations"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "app_directory": app.root_path,
        "python_version": sys.version
    })

@app.route('/product/nexus-core')
def product_nexus_core():
    try:
        now = datetime.datetime.now()
        app.logger.info("Rendering nexus-core product page")
        return render_template('product_nexus_core.html', now=now)
    except Exception as e:
        app.logger.error(f"Error rendering nexus-core product page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/product/cost-optimizer')
def product_cost_optimizer():
    try:
        now = datetime.datetime.now()
        app.logger.info("Rendering cost-optimizer product page")
        return render_template('product_cost_optimizer.html', now=now)
    except Exception as e:
        app.logger.error(f"Error rendering cost-optimizer product page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/product/compliance-reporter')
def product_compliance_reporter():
    try:
        now = datetime.datetime.now()
        app.logger.info("Rendering compliance-reporter product page")
        return render_template('product_compliance_reporter.html', now=now)
    except Exception as e:
        app.logger.error(f"Error rendering compliance-reporter product page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/product/governance-dashboard')
def product_governance_dashboard():
    try:
        now = datetime.datetime.now()
        app.logger.info("Rendering governance-dashboard product page")
        return render_template('product_governance_dashboard.html', now=now)
    except Exception as e:
        app.logger.error(f"Error rendering governance-dashboard product page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/early-access', methods=['GET', 'POST'])
def early_access():
    try:
        now = datetime.datetime.now()
        if request.method == 'POST':
            name = request.form.get('name')
            company = request.form.get('company')
            email = request.form.get('email')
            phone = request.form.get('phone')
            message = request.form.get('message')
            
            app.logger.info(f"Early access form submitted by {email}")
            # In a production environment, this would send an email to NSXearlyaccess@netrunsystems.com
            # For now, just show a success message
            flash('Thank you for your interest in our Early Access Program! We will contact you shortly.', 'success')
            return redirect(url_for('early_access'))
        
        app.logger.info("Rendering early-access page")
        return render_template('early_access.html', now=now)
    except Exception as e:
        app.logger.error(f"Error in early-access page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/blog')
def blog():
    try:
        now = datetime.datetime.now()
        posts = get_sample_blog_posts()
        app.logger.info(f"Rendering blog page with {len(posts)} posts")
        return render_template('blog.html', posts=posts, now=now)
    except Exception as e:
        app.logger.error(f"Error rendering blog page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/blog/<slug>')
def blog_post(slug):
    try:
        now = datetime.datetime.now()
        post = get_sample_blog_post(slug)
        if post:
            app.logger.info(f"Rendering blog post: {slug}")
            return render_template('blog_post.html', post=post, now=now)
        app.logger.warning(f"Blog post not found: {slug}")
        abort(404)
    except Exception as e:
        app.logger.error(f"Error rendering blog post {slug}: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/admin/blog', methods=['GET', 'POST'])
def admin_blog():
    try:
        now = datetime.datetime.now()
        app.logger.info("Admin blog functionality is disabled in this simplified version")
        flash('Blog administration is currently disabled.', 'info')
        return redirect(url_for('blog'))
    except Exception as e:
        app.logger.error(f"Error in admin blog page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    try:
        now = datetime.datetime.now()
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            app.logger.info(f"Contact form submitted by {email}")
            # In a production environment, this would send an email
            # For now, just show a success message
            flash('Thank you for your message! We will get back to you shortly.', 'success')
            return redirect(url_for('contact'))
        
        app.logger.info("Rendering contact page")
        return render_template('contact.html', now=now)
    except Exception as e:
        app.logger.error(f"Error in contact page: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception as e:
        app.logger.error(f"Error serving favicon: {str(e)}")
        return "", 404

# This is required for Azure App Service to find the application
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.logger.info(f"Starting application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
