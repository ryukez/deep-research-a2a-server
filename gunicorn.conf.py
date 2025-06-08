# Gunicorn configuration file for production
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 120
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "deep-research-agent"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload application
preload_app = True

# Graceful timeout
graceful_timeout = 30


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Deep Research Agent server is ready. Accepting connections.")


def on_exit(server):
    """Called just before the server is shut down."""
    server.log.info("Deep Research Agent server is shutting down.")
