from celery import Celery
from celery.schedules import crontab
from sqlalchemy.orm import declarative_base

# Dummy Base
Base = declarative_base()

# Celery application setup
celery_app = Celery(
    "ai_hedge_fund",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Automated Ingestion Jobs Schedule
celery_app.conf.beat_schedule = {
    'ingest-price-data-5m': {
        'task': 'ingestion_tasks.fetch_price_data',
        'schedule': crontab(minute='*/5'), # Every 5 minutes
    },
    'ingest-news-data-15m': {
        'task': 'ingestion_tasks.fetch_news_data',
        'schedule': crontab(minute='*/15'), # Every 15 minutes
    },
    'ingest-fundamentals-daily': {
        'task': 'ingestion_tasks.fetch_fundamentals',
        'schedule': crontab(hour=0, minute=0), # Midnight daily
    },
    'ingest-insider-trades-daily': {
        'task': 'ingestion_tasks.fetch_insider_trades',
        'schedule': crontab(hour=0, minute=5), # 12:05 AM daily
    },
}

import logging
logger = logging.getLogger(__name__)

# Dummy tasks to simulate ingestion
@celery_app.task(bind=True, max_retries=3, rate_limit='50/m')
def fetch_price_data(self):
    """Fetches 5-minute OHLCV candles."""
    logger.info("Successfully ingested standard OHLCV price data.")

@celery_app.task(bind=True, max_retries=3, rate_limit='20/m')
def fetch_news_data(self):
    """Fetches news headlines every 15 minutes."""
    logger.info("Successfully ingested news headlines.")

@celery_app.task(bind=True, max_retries=2)
def fetch_fundamentals(self):
    """Fetches daily fundamentals."""
    logger.info("Successfully ingested fundamental ratios.")

@celery_app.task(bind=True, max_retries=2)
def fetch_insider_trades(self):
    """Fetches daily insider transactions."""
    logger.info("Successfully ingested SEC Form 4 flow data.")
