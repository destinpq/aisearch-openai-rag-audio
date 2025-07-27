#!/usr/bin/env python
"""
Script to run Celery worker for background tasks.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
    # Import Celery app
    from celery_config import app
    
    # Start worker
    argv = [
        'worker',
        '--loglevel=info',
        '--concurrency=2',  # Number of worker processes
        '-n', 'voicerag_worker@%h',  # Worker name
    ]
    
    app.worker_main(argv) 