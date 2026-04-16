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
        
    @st.cache_data(ttl=86400) # Cache for 24 hours
    def fetch_and_run_backtest_v4():
        return run_backtest()
        
    with st.spinner("Fetching decades of historic fundamental and market data from FRED & Yahoo Finance..."):
        backtest_df, scores_df, metrics_dict, latest_prices = fetch_and_run_backtest_v4()
        
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
        st.subheader("⚡ Live Action Required Console")
        action_triggered_today = backtest_df['Action_Triggered'].iloc[-1]
        
        if action_triggered_today:
            st.error("🚨 **REBALANCE TRIGGERED TODAY!** The portfolio weights mathematically breached the >5% physical drift tolerance boundary. Execute new allocations.", icon="🚨")
        else:
            st.success("✅ **HOLD STATUS (NO ACTION REQUIRED).** The physical portfolio remains within the 5% tolerance drift band of the previously executed target.", icon="✅")
            
        with st.expander("💳 Current Target Ticket Execution Pricing", expanded=False):
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("QQQ (Nasdaq 100)", f"${latest_prices['QQQ']:.2f}")
            t2.metric("TLT (20Y+ Treasury via NTSX)", f"${latest_prices['TLT']:.2f}") # TLT proxy for NTSX component
            t3.metric("GLD (Gold)", f"${latest_prices['GLD']:.2f}")
            t4.metric("DBMF (Managed Futures)", f"${latest_prices['DBMF']:.2f}")
            
        st.markdown("---")
        st.subheader("🏆 Strategy Performance Metrics (vs 60/40)")
        st.markdown("*Metrics explicitly include **10 basis points** physical transaction friction extracted per threshold rebalance round-trip.*")
        
        mc1, mc2, mc3, mc4 = st.columns(4)
        strat_mets = metrics_dict['Strategy']
        bench_mets = metrics_dict['Benchmark']
        
        with mc1:
            st.metric("CAGR (Annualized)", f"{strat_mets['CAGR']*100:.1f}%", f"{(strat_mets['CAGR'] - bench_mets['CAGR'])*100:.1f}%")
        with mc2:
            st.metric("Max Drawdown", f"{strat_mets['Max_DD']*100:.1f}%", f"{(strat_mets['Max_DD'] - bench_mets['Max_DD'])*100:.1f}%", delta_color="inverse")
        with mc3:
            st.metric("Volatility", f"{strat_mets['Vol']*100:.1f}%", f"{(strat_mets['Vol'] - bench_mets['Vol'])*100:.1f}%", delta_color="inverse")
        with mc4:
            st.metric("Sharpe Ratio", f"{strat_mets['Sharpe']:.2f}", f"{strat_mets['Sharpe'] - bench_mets['Sharpe']:.2f}")
            
        st.markdown("---")
        st.subheader("📊 20-Year Historical Proof (Actual Data Proxy)")
        
        plot_df = pd.DataFrame({
            'Macro Engine Strategy': backtest_df['Cumulative_Return'],
            '60/40 Benchmark': backtest_df['60_40_CumRev']
        })
        st.line_chart(plot_df)
        
        st.markdown("---")
        
        with st.expander("📚 How the Macro Regime Strategy Works", expanded=False):
            st.markdown("""
            **The Institutional Macro Regime Engine** explicitly shifts capital to defensive assets or risk-seeking assets depending on a 20-point composite score built from 13 fundamental tracking datasets.
            
            Based on the trailing sum of fundamental momentum across 4 pillars (Economic Growth, Credit Spreads, Market Liquidity, and Market Trends), the model assigns one of 5 distinct Regimes:
            - **STRONG BULL (>8)**: 45% NTSX, 40% QQQ, 10% DBMF, 5% GLD
            - **BULL (>3)**: 40% NTSX, 35% QQQ, 15% DBMF, 5% GLD, 5% CASH
            - **NEUTRAL (>-3)**: 30% NTSX, 20% DBMF, 20% GLD, 30% CASH
            - **RISK OFF (>-8)**: 40% DBMF, 30% GLD, 30% CASH
            - **CRISIS (<-8)**: 50% DBMF, 30% GLD, 20% CASH
            
            *(Note: SGOV/SHV proxies Cash/Short-duration Treasuries. NTSX provides 90/60 levered SPY/TLT foundational exposure).*
            """)
            
        st.subheader("📜 Historical Execution Ledger (Last 10 Physical Trades)")
        
        # Build the historical dataframe showing weights based on the Regime
        weight_map = {
            "STRONG BULL": {"NTSX": "45%", "QQQ": "40%", "DBMF": "10%", "GLD": "5%", "CASH": "0%"},
            "BULL": {"NTSX": "40%", "QQQ": "35%", "DBMF": "15%", "GLD": "5%", "CASH": "5%"},
            "NEUTRAL": {"NTSX": "30%", "QQQ": "0%", "DBMF": "20%", "GLD": "20%", "CASH": "30%"},
            "RISK OFF": {"NTSX": "0%", "QQQ": "0%", "DBMF": "40%", "GLD": "30%", "CASH": "30%"},
            "CRISIS": {"NTSX": "0%", "QQQ": "0%", "DBMF": "50%", "GLD": "30%", "CASH": "20%"}
        }
        
        # ACTUALLY filter the dataframe purely to periods where a >5% Rebalance effectively executed
        action_log = backtest_df[backtest_df['Action_Triggered'] == True].copy()
        recent_log = action_log.tail(10)
        
        recent_log['Total Score'] = scores_df['total_score'].loc[recent_log.index].map("{:.1f}".format)
        recent_log['NTSX (90/60 SPY/TLT)'] = recent_log['Regime'].map(lambda x: weight_map.get(x, {}).get("NTSX", "0%"))
        recent_log['QQQ (Nasdaq 100)'] = recent_log['Regime'].map(lambda x: weight_map.get(x, {}).get("QQQ", "0%"))
        recent_log['DBMF (Managed Futures)'] = recent_log['Regime'].map(lambda x: weight_map.get(x, {}).get("DBMF", "0%"))
        recent_log['GLD (Gold)'] = recent_log['Regime'].map(lambda x: weight_map.get(x, {}).get("GLD", "0%"))
        recent_log['SHV (Short Treasury)'] = recent_log['Regime'].map(lambda x: weight_map.get(x, {}).get("CASH", "0%"))
        recent_log['Daily Return'] = (recent_log['Daily_Return'] * 100).map("{:.2f}%".format)
        
        st.dataframe(recent_log[['Regime', 'Total Score', 'NTSX (90/60 SPY/TLT)', 'QQQ (Nasdaq 100)', 'DBMF (Managed Futures)', 'GLD (Gold)', 'SHV (Short Treasury)', 'Daily Return']], use_container_width=True)
        
        with st.expander("🔬 Raw Indicator Signals (Last 5 Days)"):
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
    def fetch_rwra_v4():
        return run_rwra_backtest()
        
    with st.spinner("Downloading and processing real historical datasets..."):
        backtest_df, probs, latest_weights, metrics_dict, latest_prices = fetch_rwra_v4()
        
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
        st.subheader("⚡ Live Action Required Console")
        action_triggered_today = backtest_df['Action_Triggered'].iloc[-1]
        
        if action_triggered_today:
            st.error("🚨 **REBALANCE TRIGGERED TODAY!** The portfolio mathematically breached the >5% physical drift tolerance boundary. Execute the new weights below.", icon="🚨")
        else:
            st.success("✅ **HOLD STATUS (NO ACTION REQUIRED).** The physical portfolio remains within the 5% tolerance drift band of the previously executed target.", icon="✅")
            
        with st.expander("💳 Current Target Ticket Execution Pricing", expanded=False):
            t1, t2, t3, t4, t5, t6 = st.columns(6)
            t1.metric("SPY", f"${latest_prices['SPY']:.2f}")
            t2.metric("QQQ", f"${latest_prices['QQQ']:.2f}")
            t3.metric("TLT", f"${latest_prices['TLT']:.2f}")
            t4.metric("GLD", f"${latest_prices['GLD']:.2f}")
            t5.metric("DBMF", f"${latest_prices['DBMF']:.2f}")
            t6.metric("CSHI", f"${latest_prices['CSHI']:.2f}")
            
        st.markdown("---")
        st.subheader("🏆 Strategy Performance Metrics (vs 60/40)")
        st.markdown("*Metrics explicitly include **10 basis points** physical transaction friction extracted per threshold rebalance round-trip.*")
        
        mc1, mc2, mc3, mc4 = st.columns(4)
        strat_mets = metrics_dict['Strategy']
        bench_mets = metrics_dict['Benchmark']
        
        with mc1:
            st.metric("CAGR (Annualized)", f"{strat_mets['CAGR']*100:.1f}%", f"{(strat_mets['CAGR'] - bench_mets['CAGR'])*100:.1f}%")
        with mc2:
            st.metric("Max Drawdown", f"{strat_mets['Max_DD']*100:.1f}%", f"{(strat_mets['Max_DD'] - bench_mets['Max_DD'])*100:.1f}%", delta_color="inverse")
        with mc3:
            st.metric("Volatility", f"{strat_mets['Vol']*100:.1f}%", f"{(strat_mets['Vol'] - bench_mets['Vol'])*100:.1f}%", delta_color="inverse")
        with mc4:
            st.metric("Sharpe Ratio", f"{strat_mets['Sharpe']:.2f}", f"{strat_mets['Sharpe'] - bench_mets['Sharpe']:.2f}")
            
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("⚖️ Target Weights")
            weight_names_map = {
                'SPY': 'SPY (S&P 500)',
                'QQQ': 'QQQ (Nasdaq 100)',
                'TLT': 'TLT (20Y Treasury)',
                'DBMF': 'DBMF (Managed Futures)',
                'GLD': 'GLD (Gold)',
                'CSHI': 'CSHI (High Yield Cash)'
            }
            for asset, weight in latest_weights.items():
                st.markdown(f"**{weight_names_map.get(asset, asset)}**: {weight*100:.1f}%")
                st.progress(weight)
                
        with col2:
            st.subheader("📈 RWRA 20-Year Equity Curve")
            plot_df = pd.DataFrame({
                'RWRA Strategy (12.4% Target)': backtest_df['Cumulative_Return'],
                '60/40 Benchmark': backtest_df['60_40_CumRev']
            })
            st.line_chart(plot_df)
            
        st.markdown("---")
        
        st.subheader("🦅 Macro Regime Turning Points & Black Swan Ledger")
        st.markdown("*Interactive Timeline mapping mathematical regime shifts against physical global macro shocks.*")
        import altair as alt
        try:
            plot_probs = probs.copy()
            plot_probs.index.name = 'Date'
            plot_probs = plot_probs.reset_index()
            
            # Format explicitly for Altair layering
            melted_probs = plot_probs.melt('Date', var_name='Regime', value_name='Probability')
            
            swan_events = {
                "2008-09-15": "Lehman Brothers Collapse (GFC)",
                "2011-08-05": "US Credit Downgrade",
                "2015-08-24": "China Flash Crash",
                "2018-02-05": "Volmageddon (VIX Spike)",
                "2020-03-09": "COVID-19 Global Crash",
                "2022-02-24": "Russia-Ukraine War",
                "2023-03-10": "SVB Bank Collapse",
                "2024-08-05": "Yen Carry Unwind"
            }
            swan_df = pd.DataFrame(list(swan_events.items()), columns=['Date', 'Event_Narrative'])
            swan_df['Date'] = pd.to_datetime(swan_df['Date'])
            
            # 1. Base Layer Area Curve (Now Fully Interactive)
            area_chart = alt.Chart(melted_probs).mark_area(opacity=0.7).encode(
                x=alt.X('Date:T', title='Lookback Timeline (20 Years)'),
                y=alt.Y('Probability:Q', stack='normalize', title='Model Probability Allocation'),
                color=alt.Color('Regime:N', scale=alt.Scale(domain=['Bull', 'Neutral', 'Bear', 'Crisis'], 
                                                            range=['#3fb950', '#8b949e', '#d2a8ff', '#f85149'])),
                tooltip=['Date:T', 'Regime:N', alt.Tooltip('Probability:Q', format='.1%')]
            ).properties(height=500).interactive(bind_y=False) # Allow X-axis zooming and panning
            
            # 2. Black Swan Intersection Lines
            swan_rules = alt.Chart(swan_df).mark_rule(color='#ffcc00', strokeWidth=2, strokeDash=[4, 4]).encode(
                x='Date:T',
                tooltip=['Date:T', 'Event_Narrative:N']
            )
            
            # 3. Text Overlay for visually flagging the events
            swan_text = alt.Chart(swan_df).mark_text(
                align='left', baseline='middle', dx=5, dy=-210, color='#ffcc00', fontSize=12, angle=270, fontWeight='bold'
            ).encode(
                x='Date:T',
                text='Event_Narrative:N'
            )
            
            final_chart = alt.layer(area_chart, swan_rules, swan_text).resolve_scale(y='shared')
            st.altair_chart(final_chart, use_container_width=True)
            
            # Add granular dataframe view of the Swan Events
            with st.expander("📋 Expand to strictly audit the algorithm's defense during these exact Black Swan events", expanded=False):
                # Filter probabilities matrix exactly matching the dates of our Swan Dictionary
                audit_df = pd.merge(swan_df, probs, left_on='Date', right_index=True, how='inner')
                audit_df['Date'] = audit_df['Date'].dt.strftime('%Y-%m-%d')
                
                # Clean up probabilistic formatting for display
                for col in ['Bull', 'Neutral', 'Bear', 'Crisis']:
                    if col in audit_df:
                        audit_df[col] = (audit_df[col] * 100).map("{:.1f}%".format)
                        
                st.dataframe(audit_df[['Date', 'Event_Narrative', 'Crisis', 'Bear', 'Neutral', 'Bull']].set_index('Date'), use_container_width=True)
                
        except Exception as e:
            st.error(f"Failed to compile Altair rendering engine: {e}")
            
        st.markdown("---")
        # 1. Strategy Logic & How it works
        with st.expander("📚 How the RWRA Strategy Works", expanded=False):
            st.markdown("""
            **Regime-Weighted Risk Allocation (RWRA)** abandons traditional static portfolios (like 60/40) for a dynamic, mathematically pure engine that adjusts to macroeconomic reality every single day.
            
            **The Engine calculates a blend of 4 Regimes based on 5 Core Variables:**
            1. **Yield Curve (`T10Y2Y`)**: An inverted yield curve indicates recession risk.
            2. **Credit Spreads (`BAMLH0A0HYM2`)**: Rising corporate bond spreads indicate systemic stress.
            3. **Liquidity (`NFCI`)**: Tightening financial conditions restrict economic growth.
            4. **Volatility (`^VIX`)**: Market implied risk over 20 triggers bearish signals.
            5. **Price Trend (`^GSPC`)**: S&P 500 trading below its 200-day moving average confirms a downtrend.
            
            Based on how many of these indicators signal danger, the engine assigns specific **Probabilities** to four regimes: *Bull, Neutral, Bear, and Crisis*. 
            Asset weights are mathematically blended across these probabilities daily, removing human emotion.
            
            *Emergency Protocol:* If the **VIX crosses 35**, all calculations are aborted and the regime strictly locks to 100% Crisis.
            """)
            
        st.subheader("📜 Historical Execution Ledger (Last 10 Physical Trades)")
        
        # Filter purely for Action Trade dates!
        action_log = backtest_df[backtest_df['Action_Triggered'] == True].copy()
        
        # We merge backtest weights, probs and returns for the last 10 execution days
        log_df = pd.merge(probs, action_log[['RWRA_Return', 'SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI']], left_index=True, right_index=True)
        log_df = log_df.tail(10)
        
        log_df = log_df.rename(columns={
            'SPY': 'SPY (S&P 500)',
            'QQQ': 'QQQ (Nasdaq 100)',
            'TLT': 'TLT (20Y Treasury)',
            'DBMF': 'DBMF (Managed Futures)',
            'GLD': 'GLD (Gold)',
            'CSHI': 'CSHI (High Yield Cash)'
        })
        
        # Formatting for readability
        for col in ['Bull', 'Neutral', 'Bear', 'Crisis', 'SPY (S&P 500)', 'QQQ (Nasdaq 100)', 'TLT (20Y Treasury)', 'DBMF (Managed Futures)', 'GLD (Gold)', 'CSHI (High Yield Cash)']:
            log_df[col] = (log_df[col] * 100).map("{:.1f}%".format)
            
        log_df['Daily Return'] = (log_df['RWRA_Return'] * 100).map("{:.2f}%".format)
        
        st.dataframe(log_df[['Bull', 'Neutral', 'Bear', 'Crisis', 'SPY (S&P 500)', 'QQQ (Nasdaq 100)', 'TLT (20Y Treasury)', 'DBMF (Managed Futures)', 'GLD (Gold)', 'CSHI (High Yield Cash)', 'Daily Return']], use_container_width=True)
            
        st.markdown("*Emergency Protocol Note: If VIX > 35, probabilities mathematically lock to 100% Crisis.*")
