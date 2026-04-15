Challenge accepted. You’re essentially trying to slice up Wall Street’s biggest brains, isolate their sensory inputs, and shove them into a Docker container to print money. I respect the ambition. 

Let's keep this rational, clean, and straight to the point. Below is the overarching project structure, followed by the complete backend implementation for **Section 2: Data Ingestion & Database Architecture**.

### 1. Overarching Folder Structure

We are isolating concerns. FastAPI handles the REST layer, Celery handles the asynchronous ingestion/agent routing, and TimescaleDB acts as the backbone.

```text
ai_hedge_fund/
├── docker-compose.yml           # orchestrates FastAPI, Celery, Redis, TimescaleDB
├── backend/
│   ├── requirements.txt
│   ├── main.py                  # FastAPI application entry point
│   ├── core/
│   │   ├── config.py            # Environment vars & settings
│   │   ├── database.py          # SQLAlchemy + TimescaleDB engine
│   │   └── celery_app.py        # Celery & Beat configuration
│   ├── models/
│   │   └── schema.py            # 7 Database tables (SQLAlchemy)
│   ├── workers/                 # Ingestion Pipeline
│   │   ├── tasks_ingestion.py   # Celery tasks (5m, 15m, daily)
│   │   └── data_fetchers.py     # API calls to market data providers
│   ├── agents/                  # The Wall Street Brains (Wolf, Munger, etc.)
│   ├── backtest/                # Blind execution engine
│   └── api/                     # FastAPI route handlers
└── frontend/                    # Next.js visual dashboard (Future)
```

---

### 2. Database & Ingestion Code (Section 2)

We are using **SQLAlchemy** with a PostgreSQL/TimescaleDB dialect. We must explicitly convert the time-series tables into TimescaleDB *hypertables* for optimized querying.

#### `backend/models/schema.py` (Database Architecture)
Here are the 7 required tables. Notice how we isolate data types to enforce the "information asymmetry" required by your agents later.

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

# Table 1: The Watchlist (Targeting emerging sectors)
class Stock(Base):
    __tablename__ = "stocks"
    ticker = Column(String(10), primary_key=True, index=True)
    company_name = Column(String(100))
    sector = Column(String(50))
    is_active = Column(Boolean, default=True)

# Table 2: Live Price Action (For Cohen & Dalio)
class PriceData(Base):
    __tablename__ = "price_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

# Table 3: News Feed (For Munger & Dalio)
class NewsData(Base):
    __tablename__ = "news_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    headline = Column(String(255))
    sentiment_score = Column(Float) # Pre-processed LLM sentiment

# Table 4: Fundamentals (For Wolf, Munger, Aman)
class FundamentalData(Base):
    __tablename__ = "fundamentals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    pe_ratio = Column(Float)
    revenue = Column(Float)
    cash_flow = Column(Float)
    debt_to_equity = Column(Float)

# Table 5: Insider Trades (For Aman)
class InsiderTrade(Base):
    __tablename__ = "insider_trades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    executive_name = Column(String(100))
    transaction_type = Column(String(10)) # BUY / SELL
    volume = Column(Integer)

# Table 6: Agent Verdicts (Committee Consensus inputs)
class AgentVerdict(Base):
    __tablename__ = "agent_verdicts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String(50)) # Wolf, Munger, Aman, Cohen, Dalio
    verdict = Column(String(20)) # Bullish, Bearish, Neutral
    confidence = Column(Float)
    reasoning = Column(String) # LLM output

# Table 7: CIO Portfolio Allocation (Final outputs)
class PortfolioAllocation(Base):
    __tablename__ = "portfolio_allocations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ticker = Column(String(10), ForeignKey("stocks.ticker"), nullable=False)
    allocated_percentage = Column(Float)

# TimescaleDB hypertable conversion script to be run on init
def create_hypertables(engine):
    with engine.begin() as conn:
        conn.execute(text("SELECT create_hypertable('price_data', 'timestamp', if_not_exists => TRUE);"))
        conn.execute(text("SELECT create_hypertable('news_data', 'timestamp', if_not_exists => TRUE);"))
```

#### `backend/core/celery_app.py` (Task Routing & Scheduling)
This sets up the queue and the exact chronological execution schedule you requested. 

```python
from celery import Celery
from celery.schedules import crontab

# Assuming Redis is used as the message broker for Celery
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
        'task': 'workers.tasks_ingestion.fetch_price_data',
        'schedule': crontab(minute='*/5'), # Every 5 minutes
    },
    'ingest-news-data-15m': {
        'task': 'workers.tasks_ingestion.fetch_news_data',
        'schedule': crontab(minute='*/15'), # Every 15 minutes
    },
    'ingest-fundamentals-daily': {
        'task': 'workers.tasks_ingestion.fetch_fundamentals',
        'schedule': crontab(hour=0, minute=0), # Midnight daily
    },
    'ingest-insider-trades-daily': {
        'task': 'workers.tasks_ingestion.fetch_insider_trades',
        'schedule': crontab(hour=0, minute=5), # 12:05 AM daily
    },
}
```

#### `backend/workers/tasks_ingestion.py` (The Ingestion Logic)
This acts as the engine pulling data into Timescale. Rate limiting and error handling (try/except blocks with Celery retries) are baked in to prevent the API limits from crashing the pipeline.

```python
from core.celery_app import celery_app
from core.database import SessionLocal
from models.schema import Stock, PriceData, NewsData, FundamentalData, InsiderTrade
import logging

logger = logging.getLogger(__name__)

def get_watchlist(db):
    return [stock.ticker for stock in db.query(Stock).filter(Stock.is_active == True).all()]

@celery_app.task(bind=True, max_retries=3, rate_limit='50/m')
def fetch_price_data(self):
    """Fetches 5-minute OHLCV candles."""
    db = SessionLocal()
    try:
        tickers = get_watchlist(db)
        for ticker in tickers:
            # TODO: Integrate external API call (e.g., Polygon.io, YFinance)
            # mock_data = fetch_from_provider(ticker)
            
            new_price = PriceData(
                ticker=ticker,
                open=100.0, high=105.0, low=99.0, close=102.5, volume=15000 # Mock
            )
            db.add(new_price)
        db.commit()
        logger.info(f"Successfully ingested price data for {len(tickers)} tickers.")
    except Exception as exc:
        db.rollback()
        logger.error(f"Price ingestion failed: {exc}")
        raise self.retry(exc=exc, countdown=60) # Retry after 1 minute
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3, rate_limit='20/m')
def fetch_news_data(self):
    """Fetches news headlines every 15 minutes."""
    db = SessionLocal()
    try:
        tickers = get_watchlist(db)
        for ticker in tickers:
            # TODO: Fetch news API
            new_news = NewsData(
                ticker=ticker,
                headline=f"Emerging sector growth expected for {ticker}",
                sentiment_score=0.8 # Pre-computed or raw to be processed
            )
            db.add(new_news)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=120)
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=2)
def fetch_fundamentals(self):
    """Fetches daily fundamentals."""
    db = SessionLocal()
    try:
        tickers = get_watchlist(db)
        for ticker in tickers:
            # TODO: Fetch fundamentals API
            fund = FundamentalData(
                ticker=ticker, pe_ratio=25.4, revenue=5000000.0, 
                cash_flow=1200000.0, debt_to_equity=0.5
            )
            db.add(fund)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=2)
def fetch_insider_trades(self):
    """Fetches daily insider transactions."""
    db = SessionLocal()
    try:
        tickers = get_watchlist(db)
        for ticker in tickers:
            # TODO: Fetch insider trade API
            trade = InsiderTrade(
                ticker=ticker, executive_name="John Doe", 
                transaction_type="BUY", volume=5000
            )
            db.add(trade)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()
```