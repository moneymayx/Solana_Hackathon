"""
Celery Application Configuration

Sets up Celery for background task processing, including:
- Embedding generation
- Context summarization
- Pattern analysis
"""
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "billions_bounty",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Only prefetch 1 task at a time
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
    
    # Task routing
    task_routes={
        "src.celery_tasks.generate_embedding_task": {"queue": "embeddings"},
        "src.celery_tasks.create_context_summary_task": {"queue": "summaries"},
        "src.celery_tasks.analyze_patterns_task": {"queue": "analysis"},
    },
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "generate-context-summaries": {
            "task": "src.celery_tasks.generate_summaries_for_active_users",
            "schedule": 3600.0,  # Run every hour
        },
        "update-pattern-stats": {
            "task": "src.celery_tasks.update_pattern_statistics",
            "schedule": 1800.0,  # Run every 30 minutes
        },
    },
)

if __name__ == "__main__":
    celery_app.start()

