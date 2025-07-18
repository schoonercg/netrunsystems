"""Gunicorn configuration file for Azure App Service deployment"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Basic configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = 1
timeout = 600
accesslog = '-'
errorlog = '-'
loglevel = 'info'
preload_app = True

# Add the app directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

logger.info(f"Gunicorn configuration loaded - binding to {bind}")

def when_ready(server):
    """Called just after the server is started."""
    logger.info("Gunicorn server is ready. Spawning workers.")

def worker_init(worker):
    """Called just after a worker has been forked."""
    logger.info(f"Worker spawned (pid: {worker.pid})")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    logger.info(f"Worker about to be spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    logger.info(f"Worker spawned and initialized (pid: {worker.pid})")

def worker_exit(server, worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    logger.info(f"Worker exited (pid: {worker.pid})")

def on_exit(server):
    """Called just before exiting."""
    logger.info("Gunicorn server is shutting down.")