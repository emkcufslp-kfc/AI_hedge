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
