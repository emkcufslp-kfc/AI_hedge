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

# --- Sidebar Navigation ---
st.sidebar.title("🏦 Institutional Dashboard")
page = st.sidebar.radio("Navigation", ["Agent Consensus", "Macro Regime Model", "Final RWRA Engine"])

if page == "Agent Consensus":
    st.title("🏦 Institutional AI Hedge Fund - CIO Terminal")
    st.markdown("Real-time Committee Consensus & Portfolio Pipeline")

    # MOCK DATA
    tickers = ["NVDA", "TSLA", "PLTR", "AMD", "AAPL"]

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

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🤖 The Committee Actions (Live Agents)")
        selected_ticker = st.selectbox("Select Asset for Deep Dive", tickers)
        
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
        chart_data = pd.DataFrame(np.random.randn(20, 1).cumsum() + 100, columns=['Close'])
        st.line_chart(chart_data)

    st.markdown("---")
    st.markdown("*System: FastAPI / Celery / TimescaleDB (Simulated Environment). Agent operations are currently running in blind backtest mode.*")

elif page == "Macro Regime Model":
    st.title("🌍 Institutional Macro Regime Engine")
    st.markdown("20-Indicator Real-Time Scoring System & 20-Year Backtest")
    
    # We dynamically load macro_backtest
    try:
        from macro_backtest import run_backtest
    except Exception as e:
        st.error(f"Failed to import macro engine. Root cause: {str(e)}")
        st.stop()
        
    @st.cache_data(ttl=86400) # Cache for 24 hours so it only runs once per day on Streamlit Cloud
    def fetch_and_run_backtest():
        return run_backtest()
        
    with st.spinner("Fetching decades of historic fundamental and market data from FRED & Yahoo Finance..."):
        backtest_df, scores_df = fetch_and_run_backtest()
        
    if backtest_df is None or backtest_df.empty:
        st.error("Failed to fetch historical actual data. The APIs might be rate limited locally.")
    else:
        # Latest data display
        current_score = scores_df['total_score'].iloc[-1]
        current_regime = scores_df['Regime'].iloc[-1]
        
        st.markdown("### 📡 Live Risk Engine")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Current Regime</div><div class="metric-value">{current_regime}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Composite Risk Score</div><div class="metric-value">{current_score:.1f} / 20</div></div>', unsafe_allow_html=True)
        with c3:
            # Crash risk proxy based on score
            risk_pct = max(0, min(100, (1 - (current_score + 20) / 40) * 100))
            st.markdown(f'<div class="metric-card"><div class="metric-title">Systematic Crash Risk</div><div class="metric-value">{risk_pct:.1f}%</div></div>', unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("📊 20-Year Historical Proof (Actual Data Proxy)")
        
        plot_df = pd.DataFrame({
            'Macro Engine Strategy': backtest_df['Cumulative_Return'],
            '60/40 Benchmark': backtest_df['60_40_CumRev']
        })
        st.line_chart(plot_df)
        
        st.markdown("### Raw Indicator Signals (Last 5 Days)")
        st.dataframe(scores_df.tail(5))
        
        st.markdown("*Note: Uses FRED datasets (M2, LEI, Spreads) and YFinance price action proxies to ensure zero look-ahead bias spanning two decades.*")

elif page == "Final RWRA Engine":
    st.title("⚖️ Regime-Weighted Risk Allocation (RWRA)")
    st.markdown("Dynamic Probabilistic Allocation Engine (vFinal)")
    
    try:
        from rwra_backtest import run_rwra_backtest
    except Exception as e:
        st.error(f"Failed to import RWRA engine. Root cause: {str(e)}")
        st.stop()
        
    @st.cache_data(ttl=86400)
    def fetch_rwra():
        return run_rwra_backtest()
        
    with st.spinner("Downloading and processing real historical datasets..."):
        backtest_df, probs, latest_weights = fetch_rwra()
        
    if backtest_df is None or backtest_df.empty:
        st.error("Failed to fetch historical actual data for RWRA.")
    else:
        # Display Probabilities
        st.subheader("🎲 Live Regime Probabilities")
        curr_probs = probs.iloc[-1]
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Bull</div><div class="metric-value" style="color:#3fb950;">{curr_probs["Bull"]*100:.1f}%</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Neutral</div><div class="metric-value" style="color:#f0f6fc;">{curr_probs["Neutral"]*100:.1f}%</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Bear</div><div class="metric-value" style="color:#d2a8ff;">{curr_probs["Bear"]*100:.1f}%</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Crisis</div><div class="metric-value" style="color:#f85149;">{curr_probs["Crisis"]*100:.1f}%</div></div>', unsafe_allow_html=True)
            
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("⚖️ Target Weights")
            for asset, weight in latest_weights.items():
                st.markdown(f"**{asset}**: {weight*100:.1f}%")
                st.progress(weight)
                
        with col2:
            st.subheader("📈 RWRA 20-Year Equity Curve")
            plot_df = pd.DataFrame({
                'RWRA Strategy (12.4% Target)': backtest_df['Cumulative_Return'],
                '60/40 Benchmark': backtest_df['60_40_CumRev']
            })
            st.line_chart(plot_df)
            
        st.markdown("*Emergency Protocol Note: If VIX > 35, probabilities mathematically lock to 100% Crisis.*")
