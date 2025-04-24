from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/nist-assistant')
def nist_assistant():
    return render_template('nist_assistant.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # In a production environment, this would process the form data
    # For now, just redirect back to the home page
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return 'Healthy'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)

# This is required for Azure App Service
application = app
