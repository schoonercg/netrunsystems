from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Netrun Systems! This is a minimal Flask application.'

@app.route('/health')
def health():
    return 'Healthy'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

# This is required for Azure App Service
application = app
