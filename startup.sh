#!/bin/bash

echo "Starting Netrun Systems Flask application..."
echo "Environment variables:"
echo "PORT=$PORT"
echo "FLASK_ENV=$FLASK_ENV"
echo "WEBSITE_HOSTNAME=$WEBSITE_HOSTNAME"
echo "WEBSITE_INSTANCE_ID=$WEBSITE_INSTANCE_ID"

echo "Python version:"
python --version

echo "Installed packages:"
pip list

echo "Testing Flask app import..."
python -c "from app import app; print('Flask app imported successfully')"

echo "Starting gunicorn..."
exec gunicorn --config gunicorn_config.py app:app