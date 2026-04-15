import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Hedge Fund AI Dashboard", page_icon="📈", layout="wide")

# Premium CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(40, 51, 69, 0.9);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #58a6ff;
    }
    .trend-up {
        color: #3fb950;
        font-size: 1rem;
    }
    .trend-down {
        color: #f85149;
        font-size: 1rem;
    }
    .agent-box {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .agent-name {
        font-weight: bold;
        font-size: 1.1rem;
        color: #d2a8ff;
    }
    .agent-verdict-bullish { color: #3fb950; font-weight:bold; }
    .agent-verdict-bearish { color: #f85149; font-weight:bold; }
    .agent-verdict-neutral { color: #f0f6fc; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

st.title("🏦 Institutional AI Hedge Fund - CIO Terminal")
st.markdown("Real-time Committee Consensus & Portfolio Pipeline")

# MOCK DATA
tickers = ["NVDA", "TSLA", "PLTR", "AMD", "AAPL"]

# --- Section 1: Top Metrics ---
cols = st.columns(4)
with cols[0]:
    st.markdown('<div class="metric-card"><div class="metric-title">Total AUM</div><div class="metric-value">$1.24B</div><div class="trend-up">▲ 2.4%</div></div>', unsafe_allow_html=True)
with cols[1]:
    st.markdown('<div class="metric-card"><div class="metric-title">Active Positions</div><div class="metric-value">14</div><div class="trend-up">▲ 1</div></div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown('<div class="metric-card"><div class="metric-title">Pipeline Health</div><div class="metric-value">99.9%</div><div class="trend-up">Stable</div></div>', unsafe_allow_html=True)
with cols[3]:
    st.markdown('<div class="metric-card"><div class="metric-title">Daily Alpha</div><div class="metric-value">+42 bps</div><div class="trend-up">▲ 12 bps</div></div>', unsafe_allow_html=True)

st.markdown("---")

# --- Section 2: Agent Consensus & Live Tickers ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🤖 The Committee Actions (Live Agents)")
    selected_ticker = st.selectbox("Select Asset for Deep Dive", tickers)
    
    # Mocking Agent Views
    st.markdown(f'<div class="agent-box"><span class="agent-name">Wolf (Fundamentals):</span> Reviewed {selected_ticker} PE/Revenue. <br>Verdict: <span class="agent-verdict-bullish">BULLISH</span> (Confidence: 85%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="agent-box"><span class="agent-name">Munger (Value/News):</span> Processed recent sector data for {selected_ticker}. <br>Verdict: <span class="agent-verdict-neutral">NEUTRAL</span> (Confidence: 60%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="agent-box"><span class="agent-name">Aman (Insider Flow):</span> Detected executive share acquisition in last 48hr. <br>Verdict: <span class="agent-verdict-bullish">BULLISH</span> (Confidence: 92%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="agent-box"><span class="agent-name">Cohen (Price Action):</span> Momentum flags triggered on 5m candles. <br>Verdict: <span class="agent-verdict-bullish">BULLISH</span> (Confidence: 78%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="agent-box"><span class="agent-name">Dalio (Macro/Risk):</span> Adjusted for market beta and sector volatility. <br>Verdict: <span class="agent-verdict-bearish">BEARISH</span> (Confidence: 55%)</div>', unsafe_allow_html=True)
    
with col2:
    st.subheader("CIO Final Allocation")
    st.markdown(f"**Target Asset:** {selected_ticker}")
    allocation = np.random.randint(5, 15)
    st.progress(allocation / 100.0)
    st.markdown(f"**Allocated:** {allocation}% of Portfolio")
    
    st.subheader("Latest Ingested Candles")
    # Mock Price Chart
    chart_data = pd.DataFrame(
        np.random.randn(20, 1).cumsum() + 100,
        columns=['Close']
    )
    st.line_chart(chart_data)

st.markdown("---")
st.markdown("*System: FastAPI / Celery / TimescaleDB (Simulated Environment). Agent operations are currently running in blind backtest mode.*")
