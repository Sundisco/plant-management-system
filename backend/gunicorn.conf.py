import multiprocessing
import os

# Gunicorn config
bind = "0.0.0.0:" + str(os.getenv("PORT", "8000"))
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120  # Increase timeout to 120 seconds
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 120
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Worker configuration
worker_connections = 1000
worker_tmp_dir = "/dev/shm"  # Use shared memory for temporary files
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 120
graceful_timeout = 120
keepalive = 5

# Process naming
proc_name = "plant_management_api"

# SSL (if needed)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 