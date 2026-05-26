import datetime

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Hedge Fund AI Dashboard", page_icon="HF", layout="wide")


st.markdown(
    """
<style>
    .stApp {
        background-color: #000000;
        color: #f0f6fc;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .metric-card {
        background: linear-gradient(145deg, #0f0f0f, #050505);
        border: 1px solid rgba(0, 242, 255, 0.2);
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(0, 242, 255, 0.8);
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 12px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #00f2ff;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.3);
    }
    .trend-up {
        color: #00ff88;
        font-size: 1rem;
        font-weight: bold;
    }
    .trend-down {
        color: #ff3333;
        font-size: 1rem;
        font-weight: bold;
    }
    .agent-box {
        background: #0a0a0a;
        border-left: 4px solid #58a6ff;
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.4);
    }
    .agent-name {
        font-weight: 900;
        font-size: 1rem;
        color: #d2a8ff;
        text-transform: uppercase;
    }
    .agent-verdict-bullish { color: #00ff88; font-weight:bold; }
    .agent-verdict-bearish { color: #ff3333; font-weight:bold; }
    .agent-verdict-neutral { color: #8b949e; font-weight:bold; }
    .pit-banner {
        background:
            radial-gradient(circle at top left, rgba(0, 242, 255, 0.16), transparent 36%),
            linear-gradient(135deg, rgba(9, 16, 24, 0.96), rgba(19, 10, 28, 0.96));
        border: 1px solid rgba(0, 242, 255, 0.32);
        box-shadow: 0 18px 35px rgba(0, 0, 0, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    .pit-banner-title {
        color: #00f2ff;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .pit-banner-body {
        color: #f0f6fc;
        font-size: 0.95rem;
        line-height: 1.55;
    }
    .page-shell {
        background:
            radial-gradient(circle at top right, rgba(0, 242, 255, 0.08), transparent 28%),
            linear-gradient(180deg, rgba(8, 12, 18, 0.92), rgba(5, 7, 12, 0.94));
        border: 1px solid rgba(88, 166, 255, 0.12);
        border-radius: 20px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 22px 40px rgba(0, 0, 0, 0.22);
    }
    .section-kicker {
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        font-size: 0.76rem;
        margin-bottom: 8px;
    }
    .sidebar-shell {
        background:
            radial-gradient(circle at top left, rgba(0, 242, 255, 0.10), transparent 32%),
            linear-gradient(165deg, rgba(13, 18, 25, 0.96), rgba(7, 10, 16, 0.98));
        border: 1px solid rgba(88, 166, 255, 0.14);
        border-radius: 18px;
        padding: 14px 14px 10px 14px;
        margin: 8px 0 16px 0;
        box-shadow: 0 18px 32px rgba(0, 0, 0, 0.28);
    }
    .sidebar-pit-title {
        color: #f0f6fc;
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 4px;
    }
    .sidebar-pit-label {
        color: #00f2ff;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.72rem;
        margin-bottom: 8px;
    }
    .sidebar-pit-copy {
        color: #9fb0c3;
        font-size: 0.84rem;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    .sidebar-pit-active {
        margin-top: 12px;
        padding: 10px 12px;
        border-radius: 12px;
        background: rgba(0, 242, 255, 0.08);
        border: 1px solid rgba(0, 242, 255, 0.2);
        color: #f0f6fc;
        font-size: 0.84rem;
    }
    .sidebar-nav-label {
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.72rem;
        margin: 2px 0 10px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=86400)
def load_market_data():
    return pd.read_csv("data/historical_market.csv", index_col=0, parse_dates=True).sort_index()


@st.cache_data(ttl=86400)
def load_macro_data():
    return pd.read_csv("data/historical_macro.csv", index_col=0, parse_dates=True).sort_index()


@st.cache_data(ttl=86400)
def load_global_pit_calendar():
    market_df = load_market_data()
    macro_df = load_macro_data()
    return market_df.index.intersection(macro_df.index).sort_values()


def compute_display_metrics(series):
    clean_series = pd.Series(series).dropna()
    if clean_series.empty:
        return {"CAGR": 0.0, "Vol": 0.0, "Sharpe": 0.0, "Max_DD": 0.0}

    days = len(clean_series)
    years = days / 252 if days else 0
    cumulative_return = (1 + clean_series).prod()
    cagr = (cumulative_return ** (1 / years) - 1) if years > 0 else 0.0
    volatility = clean_series.std() * np.sqrt(252)
    sharpe = cagr / volatility if volatility > 0 else 0.0

    cumprod_series = (1 + clean_series).cumprod()
    rolling_max = cumprod_series.cummax()
    drawdowns = cumprod_series / rolling_max - 1
    max_drawdown = drawdowns.min() if not drawdowns.empty else 0.0

    return {"CAGR": cagr, "Vol": volatility, "Sharpe": sharpe, "Max_DD": max_drawdown}


def resolve_pit_date(index, requested_date):
    date_index = pd.DatetimeIndex(index).sort_values().normalize().unique()
    requested_ts = pd.Timestamp(requested_date).normalize()

    if len(date_index) == 0:
        return None, "unavailable"

    prior_dates = date_index[date_index <= requested_ts]
    if len(prior_dates) == 0:
        return date_index[0], "earliest_available"

    resolved_date = prior_dates[-1]
    if resolved_date == requested_ts:
        return resolved_date, "exact"
    return resolved_date, "prior_available"


def format_date(ts):
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def render_pit_banner(requested_date, resolved_date, resolution_reason, note):
    message = f"Viewing dashboard as of {format_date(resolved_date)} (PIT)."
    if resolution_reason == "prior_available":
        message = (
            f"Requested {format_date(requested_date)}. "
            f"Using nearest prior available date {format_date(resolved_date)}."
        )
    elif resolution_reason == "earliest_available":
        message = (
            f"Requested {format_date(requested_date)} before data inception. "
            f"Using earliest available date {format_date(resolved_date)}."
        )

    st.markdown(
        f"""
<div class="pit-banner">
    <div class="pit-banner-title">Point-In-Time View</div>
    <div class="pit-banner-body">{message}<br>{note}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def init_pit_state():
    pit_calendar = load_global_pit_calendar()
    if len(pit_calendar) == 0:
        st.error("No PIT calendar could be built from the local cached data.")
        st.stop()

    earliest_date = pit_calendar.min().date()
    latest_date = pit_calendar.max().date()

    if "pit_committed_date" not in st.session_state:
        st.session_state["pit_committed_date"] = latest_date
    if "pit_date_picker" not in st.session_state:
        st.session_state["pit_date_picker"] = st.session_state["pit_committed_date"]

    st.sidebar.markdown(
        """
<div class="sidebar-shell">
    <div class="sidebar-pit-label">Point-In-Time</div>
    <div class="sidebar-pit-title">Historical Dashboard Lens</div>
    <div class="sidebar-pit-copy">Display-only control. This changes which historical snapshot the dashboard shows and does not modify model logic or backend modules.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.sidebar.date_input(
        "PIT Date",
        min_value=earliest_date,
        max_value=latest_date,
        key="pit_date_picker",
    )
    st.sidebar.caption(f"Latest available data date: {latest_date}")
    st.sidebar.caption("If a selected date is unavailable, the dashboard resolves to the nearest prior valid date.")

    if st.sidebar.button("Update", use_container_width=True):
        st.session_state["pit_committed_date"] = st.session_state["pit_date_picker"]

    requested_date = st.session_state["pit_committed_date"]
    resolved_global_date, global_reason = resolve_pit_date(pit_calendar, requested_date)

    st.sidebar.markdown(
        f"""
<div class="sidebar-pit-active">
    <strong>Active PIT</strong><br>
    {format_date(resolved_global_date)}
</div>
""",
        unsafe_allow_html=True,
    )
    if global_reason != "exact":
        st.sidebar.caption(f"Requested `{requested_date}` and resolved to the nearest valid date.")

    return requested_date, resolved_global_date


def get_prices_for_date(columns, requested_date):
    market_df = load_market_data()
    resolved_date, _ = resolve_pit_date(market_df.index, requested_date)
    return market_df.loc[resolved_date, columns], resolved_date


st.sidebar.markdown(
    '<h1 style="color:#00f2ff; font-size:1.5rem; text-shadow: 0 0 10px rgba(0,242,255,0.5);">CIO TERMINAL</h1>',
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
<div style="background:rgba(0,242,255,0.1); border:1px solid #00f2ff; border-radius:8px; padding:10px; text-align:center; margin-bottom:20px;">
    <span style="color:#00f2ff; font-size:0.7rem; text-transform:uppercase; letter-spacing:2px;">System Status</span><br>
    <span style="color:#00ff88; font-weight:bold; font-size:1rem;">LIVE CONNECTION</span>
</div>
""",
    unsafe_allow_html=True,
)

requested_pit_date, global_pit_date = init_pit_state()

st.sidebar.markdown('<div class="sidebar-nav-label">Navigation</div>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "Navigation",
    ["Agent Consensus", "Macro Regime Model", "Final RWRA Engine", "Comparative Strategy Audit"],
    label_visibility="collapsed",
)


if page == "Agent Consensus":
    render_pit_banner(
        requested_pit_date,
        global_pit_date,
        "exact" if pd.Timestamp(requested_pit_date) == pd.Timestamp(global_pit_date) else "prior_available",
        "This page remains a simulated committee dashboard; PIT aligns the display snapshot only.",
    )
    st.markdown(
        '<h1 style="color:#00f2ff; text-shadow: 0 0 20px rgba(0,242,255,0.5); font-weight:800;">Institutional AI Hedge Fund</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#8b949e; letter-spacing:2px; text-transform:uppercase; font-size:0.8rem;'>CIO Terminal | Committee Consensus Pipeline</p>",
        unsafe_allow_html=True,
    )

    tickers = ["NVDA", "TSLA", "PLTR", "AMD", "AAPL"]
    rng = np.random.default_rng(int(global_pit_date.strftime("%Y%m%d")))
    total_aum = 1.15 + rng.uniform(0.05, 0.18)
    active_positions = int(rng.integers(11, 16))
    daily_alpha = int(rng.integers(18, 58))
    aum_delta = rng.uniform(1.2, 3.0)
    allocation = int(rng.integers(5, 15))

    cols = st.columns(4)
    with cols[0]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-title">Total AUM</div><div class="metric-value">${total_aum:.2f}B</div><div class="trend-up">+{aum_delta:.1f}%</div></div>',
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-title">Active Positions</div><div class="metric-value">{active_positions}</div><div class="trend-up">PIT View</div></div>',
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown(
            '<div class="metric-card"><div class="metric-title">Pipeline Health</div><div class="metric-value">99.9%</div><div class="trend-up">Stable</div></div>',
            unsafe_allow_html=True,
        )
    with cols[3]:
        st.markdown(
            f'<div class="metric-card"><div class="metric-title">Daily Alpha</div><div class="metric-value">+{daily_alpha} bps</div><div class="trend-up">As of PIT</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("The Committee Actions")
        selected_ticker = st.selectbox("Select Asset for Deep Dive", tickers)
        st.markdown(
            f'<div class="agent-box" style="border-color:#00f2ff;"><span class="agent-name">Wolf (Fundamentals):</span> Reviewed {selected_ticker} valuation and operating trend as of the PIT date. <br>Verdict: <span class="agent-verdict-bullish">BULLISH</span> (Confidence: 85%)</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="agent-box" style="border-color:#8b949e;"><span class="agent-name">Munger (Value/News):</span> Processed sector context available through the PIT date for {selected_ticker}. <br>Verdict: <span class="agent-verdict-neutral">NEUTRAL</span> (Confidence: 60%)</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="agent-box" style="border-color:#00ff88;"><span class="agent-name">Aman (Insider Flow):</span> Reviewed insider-flow snapshot available through the PIT date. <br>Verdict: <span class="agent-verdict-bullish">BULLISH</span> (Confidence: 92%)</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="agent-box" style="border-color:#58a6ff;"><span class="agent-name">Cohen (Price Action):</span> Momentum flags shown for the PIT snapshot in {selected_ticker}. <br>Verdict: <span class="agent-verdict-bullish">BULLISH</span> (Confidence: 78%)</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="agent-box" style="border-color:#ff3333;"><span class="agent-name">Dalio (Macro/Risk):</span> Adjusted for market beta and sector volatility known at the PIT date. <br>Verdict: <span class="agent-verdict-bearish">BEARISH</span> (Confidence: 55%)</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.subheader("CIO Final Allocation")
        st.markdown(f"**Target Asset:** {selected_ticker}")
        st.progress(allocation / 100.0)
        st.markdown(f"**Allocated:** {allocation}% of Portfolio")

        st.subheader("Ingested Candles as of PIT Date")
        chart_seed = pd.Series(rng.normal(0, 1, 20)).cumsum() + 100
        chart_data = pd.DataFrame({"Close": chart_seed})
        st.line_chart(chart_data)

    st.markdown("---")
    st.markdown(
        "*System: FastAPI / Celery / TimescaleDB (Simulated Environment). PIT changes the dashboard snapshot only.*"
    )


elif page == "Macro Regime Model":
    st.title("Institutional Macro Regime Engine")
    st.markdown("20-Indicator Real-Time Scoring System and 20-Year Backtest")

    try:
        from macro_backtest import run_backtest
    except Exception as exc:
        st.error(f"Failed to import macro engine. Root cause: {exc}")
        st.stop()

    @st.cache_data(ttl=86400)
    def fetch_and_run_backtest():
        return run_backtest()

    with st.spinner("Fetching historic fundamental and market data from the local cache..."):
        backtest_df, scores_df, _, _ = fetch_and_run_backtest()

    if backtest_df is None or backtest_df.empty or scores_df is None or scores_df.empty:
        st.error("Failed to load macro regime data from the local cache.")
    else:
        macro_dates = backtest_df.index.intersection(scores_df.index).sort_values()
        resolved_date, resolution_reason = resolve_pit_date(macro_dates, requested_pit_date)
        pit_backtest = backtest_df.loc[:resolved_date].copy()
        pit_scores = scores_df.loc[:resolved_date].copy()
        current_score = pit_scores.loc[resolved_date, "total_score"]
        current_regime = pit_scores.loc[resolved_date, "Regime"]
        current_action = bool(pit_backtest.loc[resolved_date, "Action_Triggered"])
        macro_metrics = {
            "Strategy": compute_display_metrics(pit_backtest["Daily_Return"]),
            "Benchmark": compute_display_metrics(pit_backtest["60_40_Ret"]),
        }
        macro_prices, macro_price_date = get_prices_for_date(["QQQ", "TLT", "GLD", "DBMF"], resolved_date)

        render_pit_banner(
            requested_pit_date,
            resolved_date,
            resolution_reason,
            "Display layer only. Strategy logic and macro engine modules remain unchanged.",
        )

        regime_colors = {
            "STRONG BULL": "#00ff88",
            "BULL": "#58a6ff",
            "NEUTRAL": "#8b949e",
            "RISK OFF": "#d2a8ff",
            "CRISIS": "#ff3333",
        }
        accent = regime_colors.get(current_regime, "#00f2ff")

        st.markdown(f"### <span style='color:{accent};'>PIT Risk Engine</span>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="metric-card" style="border-color:{accent};"><div class="metric-title">Current Regime</div><div class="metric-value" style="color:{accent};">{current_regime}</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-title">Composite Risk Score</div><div class="metric-value">{current_score:.1f} / 20</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            risk_pct = max(0, min(100, (1 - (current_score + 20) / 40) * 100))
            risk_color = "#ff3333" if risk_pct > 50 else "#00ff88" if risk_pct < 20 else "#00f2ff"
            st.markdown(
                f'<div class="metric-card" style="border-color:{risk_color};"><div class="metric-title">Systematic Crash Risk</div><div class="metric-value" style="color:{risk_color};">{risk_pct:.1f}%</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.subheader("Action Required Console")
        if current_action:
            st.error(
                "Rebalance triggered on the PIT date. The portfolio weights breached the >5% physical drift tolerance boundary.",
                icon="⚠️",
            )
        else:
            st.success(
                "Hold status on the PIT date. The portfolio remained within the 5% tolerance drift band.",
                icon="✅",
            )

        with st.expander("Target Ticket Execution Pricing", expanded=False):
            st.caption(f"Price snapshot date: {format_date(macro_price_date)}")
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("QQQ (Nasdaq 100)", f"${macro_prices['QQQ']:.2f}")
            t2.metric("TLT (20Y+ Treasury via NTSX)", f"${macro_prices['TLT']:.2f}")
            t3.metric("GLD (Gold)", f"${macro_prices['GLD']:.2f}")
            t4.metric("DBMF (Managed Futures)", f"${macro_prices['DBMF']:.2f}")

        st.markdown("---")
        st.subheader("Strategy Performance Metrics (vs 60/40)")
        st.markdown("*Metrics are recomputed from history available through the PIT date only.*")

        mc1, mc2, mc3, mc4 = st.columns(4)
        strat_mets = macro_metrics["Strategy"]
        bench_mets = macro_metrics["Benchmark"]
        with mc1:
            st.metric("CAGR (Annualized)", f"{strat_mets['CAGR'] * 100:.1f}%", f"{(strat_mets['CAGR'] - bench_mets['CAGR']) * 100:.1f}%")
        with mc2:
            st.metric("Max Drawdown", f"{strat_mets['Max_DD'] * 100:.1f}%", f"{(strat_mets['Max_DD'] - bench_mets['Max_DD']) * 100:.1f}%", delta_color="inverse")
        with mc3:
            st.metric("Volatility", f"{strat_mets['Vol'] * 100:.1f}%", f"{(strat_mets['Vol'] - bench_mets['Vol']) * 100:.1f}%", delta_color="inverse")
        with mc4:
            st.metric("Sharpe Ratio", f"{strat_mets['Sharpe']:.2f}", f"{strat_mets['Sharpe'] - bench_mets['Sharpe']:.2f}")

        st.markdown("---")
        st.subheader("Historical Proof Through the PIT Date")
        plot_df = pd.DataFrame(
            {
                "Macro Engine Strategy": pit_backtest["Cumulative_Return"],
                "60/40 Benchmark": pit_backtest["60_40_CumRev"],
            }
        )
        st.line_chart(plot_df)

        st.markdown("---")
        with st.expander("How the Macro Regime Strategy Works", expanded=False):
            st.markdown(
                """
                **The Institutional Macro Regime Engine** shifts capital between defensive and risk-seeking assets based on a 20-point composite score built from 13 structural inputs.

                Based on the trailing signal mix across Economic Growth, Credit Spreads, Market Liquidity, and Market Trends, the model assigns one of five regimes:
                - **STRONG BULL (>8)**: 45% NTSX, 40% QQQ, 10% DBMF, 5% GLD
                - **BULL (>3)**: 40% NTSX, 35% QQQ, 15% DBMF, 5% GLD, 5% CASH
                - **NEUTRAL (>-3)**: 30% NTSX, 20% DBMF, 20% GLD, 30% CASH
                - **RISK OFF (>-8)**: 40% DBMF, 30% GLD, 30% CASH
                - **CRISIS (<-8)**: 50% DBMF, 30% GLD, 20% CASH
                """
            )

        st.subheader("Historical Execution Ledger (Last 3 Years Relative to PIT)")
        weight_map = {
            "STRONG BULL": {"NTSX": "45%", "QQQ": "40%", "DBMF": "10%", "GLD": "5%", "CASH": "0%"},
            "BULL": {"NTSX": "40%", "QQQ": "35%", "DBMF": "15%", "GLD": "5%", "CASH": "5%"},
            "NEUTRAL": {"NTSX": "30%", "QQQ": "0%", "DBMF": "20%", "GLD": "20%", "CASH": "30%"},
            "RISK OFF": {"NTSX": "0%", "QQQ": "0%", "DBMF": "40%", "GLD": "30%", "CASH": "30%"},
            "CRISIS": {"NTSX": "0%", "QQQ": "0%", "DBMF": "50%", "GLD": "30%", "CASH": "20%"},
        }

        action_log = pit_backtest[pit_backtest["Action_Triggered"]].copy()
        three_years_ago = pd.Timestamp(resolved_date) - pd.DateOffset(years=3)
        recent_log = action_log[action_log.index >= three_years_ago].copy()
        if recent_log.empty:
            recent_log = action_log.tail(5).copy()

        recent_log["Total Score"] = pit_scores["total_score"].loc[recent_log.index].map("{:.1f}".format)
        recent_log["NTSX (90/60 SPY/TLT)"] = recent_log["Regime"].map(lambda x: weight_map.get(x, {}).get("NTSX", "0%"))
        recent_log["QQQ (Nasdaq 100)"] = recent_log["Regime"].map(lambda x: weight_map.get(x, {}).get("QQQ", "0%"))
        recent_log["DBMF (Managed Futures)"] = recent_log["Regime"].map(lambda x: weight_map.get(x, {}).get("DBMF", "0%"))
        recent_log["GLD (Gold)"] = recent_log["Regime"].map(lambda x: weight_map.get(x, {}).get("GLD", "0%"))
        recent_log["SHV (Short Treasury)"] = recent_log["Regime"].map(lambda x: weight_map.get(x, {}).get("CASH", "0%"))
        recent_log["Turnover"] = (recent_log["Turnover"] * 100).map("{:.1f}%".format)
        recent_log["Daily Return"] = (recent_log["Daily_Return"] * 100).map("{:.2f}%".format)
        recent_log = recent_log.rename_axis("Date").reset_index()
        recent_log["Execution Date"] = recent_log["Date"].dt.strftime("%b %d, %Y")

        st.dataframe(
            recent_log[
                [
                    "Execution Date",
                    "Regime",
                    "Total Score",
                    "NTSX (90/60 SPY/TLT)",
                    "QQQ (Nasdaq 100)",
                    "DBMF (Managed Futures)",
                    "GLD (Gold)",
                    "SHV (Short Treasury)",
                    "Turnover",
                    "Daily Return",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("Raw Indicator Signals (Last 5 PIT Days)"):
            st.dataframe(pit_scores.tail(5), use_container_width=True)

        st.markdown("*Note: PIT filtering is applied in the dashboard only; the macro engine logic is unchanged.*")


elif page == "Final RWRA Engine":
    st.markdown(
        '<h1 style="color:#d2a8ff; text-shadow: 0 0 20px rgba(210,168,255,0.4); font-weight:800;">Regime-Weighted Risk Allocation</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#8b949e; letter-spacing:2px; text-transform:uppercase; font-size:0.8rem;'>Dynamic Probabilistic Allocation Engine</p>",
        unsafe_allow_html=True,
    )

    try:
        from rwra_backtest import run_rwra_backtest
    except Exception as exc:
        st.error(f"Failed to import RWRA engine. Root cause: {exc}")
        st.stop()

    @st.cache_data(ttl=86400)
    def fetch_rwra():
        return run_rwra_backtest()

    with st.spinner("Loading real historical datasets from the local cache..."):
        backtest_df, probs, _, _, _ = fetch_rwra()

    if backtest_df is None or backtest_df.empty or probs is None or probs.empty:
        st.error("Failed to fetch historical actual data for RWRA.")
    else:
        rwra_dates = backtest_df.index.intersection(probs.index).sort_values()
        resolved_date, resolution_reason = resolve_pit_date(rwra_dates, requested_pit_date)
        pit_backtest = backtest_df.loc[:resolved_date].copy()
        pit_probs = probs.loc[:resolved_date].copy()
        curr_probs = pit_probs.loc[resolved_date]
        current_action = bool(pit_backtest.loc[resolved_date, "Action_Triggered"])
        current_weights = pit_backtest.loc[resolved_date, ["SPY", "QQQ", "TLT", "DBMF", "GLD", "CSHI"]].to_dict()
        rwra_metrics = {
            "Strategy": compute_display_metrics(pit_backtest["RWRA_Return"]),
            "Benchmark": compute_display_metrics(pit_backtest["60_40_Ret"]),
        }
        rwra_prices, rwra_price_date = get_prices_for_date(["SPY", "QQQ", "TLT", "GLD", "DBMF", "CSHI"], resolved_date)

        render_pit_banner(
            requested_pit_date,
            resolved_date,
            resolution_reason,
            "Display layer only. Underlying RWRA modules and strategy logic remain unchanged.",
        )

        st.subheader("PIT Regime Probabilities")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f'<div class="metric-card" style="border-color:#00ff88;"><div class="metric-title">Bull</div><div class="metric-value" style="color:#00ff88;">{curr_probs["Bull"] * 100:.1f}%</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="metric-card" style="border-color:#8b949e;"><div class="metric-title">Neutral</div><div class="metric-value" style="color:#f0f6fc;">{curr_probs["Neutral"] * 100:.1f}%</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="metric-card" style="border-color:#d2a8ff;"><div class="metric-title">Bear</div><div class="metric-value" style="color:#d2a8ff;">{curr_probs["Bear"] * 100:.1f}%</div></div>',
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f'<div class="metric-card" style="border-color:#ff3333;"><div class="metric-title">Crisis</div><div class="metric-value" style="color:#ff3333;">{curr_probs["Crisis"] * 100:.1f}%</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.subheader("Action Required Console")
        if current_action:
            st.error(
                "Rebalance triggered on the PIT date. The portfolio breached the >5% physical drift tolerance boundary.",
                icon="⚠️",
            )
        else:
            st.success(
                "Hold status on the PIT date. The portfolio remained within the 5% tolerance drift band.",
                icon="✅",
            )

        with st.expander("Target Ticket Execution Pricing", expanded=False):
            st.caption(f"Price snapshot date: {format_date(rwra_price_date)}")
            t1, t2, t3, t4, t5, t6 = st.columns(6)
            t1.metric("SPY", f"${rwra_prices['SPY']:.2f}")
            t2.metric("QQQ", f"${rwra_prices['QQQ']:.2f}")
            t3.metric("TLT", f"${rwra_prices['TLT']:.2f}")
            t4.metric("GLD", f"${rwra_prices['GLD']:.2f}")
            t5.metric("DBMF", f"${rwra_prices['DBMF']:.2f}")
            t6.metric("CSHI", f"${rwra_prices['CSHI']:.2f}")

        st.markdown("---")
        st.subheader("Strategy Performance Metrics (vs 60/40)")
        st.markdown("*Metrics are recomputed from history available through the PIT date only.*")

        mc1, mc2, mc3, mc4 = st.columns(4)
        strat_mets = rwra_metrics["Strategy"]
        bench_mets = rwra_metrics["Benchmark"]
        with mc1:
            st.metric("CAGR (Annualized)", f"{strat_mets['CAGR'] * 100:.1f}%", f"{(strat_mets['CAGR'] - bench_mets['CAGR']) * 100:.1f}%")
        with mc2:
            st.metric("Max Drawdown", f"{strat_mets['Max_DD'] * 100:.1f}%", f"{(strat_mets['Max_DD'] - bench_mets['Max_DD']) * 100:.1f}%", delta_color="inverse")
        with mc3:
            st.metric("Volatility", f"{strat_mets['Vol'] * 100:.1f}%", f"{(strat_mets['Vol'] - bench_mets['Vol']) * 100:.1f}%", delta_color="inverse")
        with mc4:
            st.metric("Sharpe Ratio", f"{strat_mets['Sharpe']:.2f}", f"{strat_mets['Sharpe'] - bench_mets['Sharpe']:.2f}")

        st.markdown("---")
        col1, col2 = st.columns([1, 2])
        weight_names_map = {
            "SPY": "SPY (S&P 500)",
            "QQQ": "QQQ (Nasdaq 100)",
            "TLT": "TLT (20Y Treasury)",
            "DBMF": "DBMF (Managed Futures)",
            "GLD": "GLD (Gold)",
            "CSHI": "CSHI (High Yield Cash)",
        }
        with col1:
            st.subheader("PIT Weights")
            for asset, weight in current_weights.items():
                st.markdown(f"**{weight_names_map.get(asset, asset)}**: {weight * 100:.1f}%")
                st.progress(float(weight))

        with col2:
            st.subheader("RWRA Equity Curve Through PIT Date")
            plot_df = pd.DataFrame(
                {
                    "RWRA Strategy (12.4% Target)": pit_backtest["Cumulative_Return"],
                    "60/40 Benchmark": pit_backtest["60_40_CumRev"],
                }
            )
            st.line_chart(plot_df)

        st.markdown("---")
        st.subheader("Macro Regime Turning Points and Black Swan Ledger")
        st.markdown("*Interactive timeline filtered through the PIT date.*")

        plot_probs = pit_probs.copy()
        plot_probs.index.name = "Date"
        plot_probs = plot_probs.reset_index()
        melted_probs = plot_probs.melt("Date", var_name="Regime", value_name="Probability")

        swan_events = {
            "2008-09-15": "Lehman Brothers Collapse (GFC)",
            "2011-08-05": "US Credit Downgrade",
            "2015-08-24": "China Flash Crash",
            "2018-02-05": "Volmageddon (VIX Spike)",
            "2020-03-09": "COVID-19 Global Crash",
            "2022-02-24": "Russia-Ukraine War",
            "2023-03-10": "SVB Bank Collapse",
            "2024-08-05": "Yen Carry Unwind",
        }
        swan_df = pd.DataFrame(list(swan_events.items()), columns=["Date", "Event_Narrative"])
        swan_df["Date"] = pd.to_datetime(swan_df["Date"])
        swan_df = swan_df[swan_df["Date"] <= resolved_date]

        area_chart = alt.Chart(melted_probs).mark_area(opacity=0.7).encode(
            x=alt.X("Date:T", title="Lookback Timeline"),
            y=alt.Y("Probability:Q", stack="normalize", title="Model Probability Allocation"),
            color=alt.Color(
                "Regime:N",
                scale=alt.Scale(
                    domain=["Bull", "Neutral", "Bear", "Crisis"],
                    range=["#00ff88", "#8b949e", "#d2a8ff", "#ff3333"],
                ),
            ),
            tooltip=["Date:T", "Regime:N", alt.Tooltip("Probability:Q", format=".1%")],
        ).properties(height=500).interactive(bind_y=False)

        swan_rules = alt.Chart(swan_df).mark_rule(color="#ffcc00", strokeWidth=2, strokeDash=[4, 4]).encode(
            x="Date:T",
            tooltip=["Date:T", "Event_Narrative:N"],
        )

        swan_text = alt.Chart(swan_df).mark_text(
            align="left",
            baseline="middle",
            dx=5,
            dy=-210,
            color="#ffcc00",
            fontSize=12,
            angle=270,
            fontWeight="bold",
        ).encode(x="Date:T", text="Event_Narrative:N")

        st.altair_chart(alt.layer(area_chart, swan_rules, swan_text).resolve_scale(y="shared"), use_container_width=True)

        with st.expander("Audit the algorithm's posture during these exact Black Swan events", expanded=False):
            audit_df = pd.merge(swan_df, pit_probs, left_on="Date", right_index=True, how="inner")
            if audit_df.empty:
                st.info("No Black Swan event rows are available on or before the selected PIT date.")
            else:
                audit_df["Date"] = audit_df["Date"].dt.strftime("%Y-%m-%d")
                for col in ["Bull", "Neutral", "Bear", "Crisis"]:
                    audit_df[col] = (audit_df[col] * 100).map("{:.1f}%".format)
                st.dataframe(
                    audit_df[["Date", "Event_Narrative", "Crisis", "Bear", "Neutral", "Bull"]].set_index("Date"),
                    use_container_width=True,
                )

        st.markdown("---")
        with st.expander("How the RWRA Strategy Works", expanded=False):
            st.markdown(
                """
                **Regime-Weighted Risk Allocation (RWRA)** replaces static 60/40 logic with a daily probabilistic blend across Bull, Neutral, Bear, and Crisis regimes.

                Core variables:
                1. **Yield Curve (`T10Y2Y`)**
                2. **Credit Spreads (`BAMLH0A0HYM2`)**
                3. **Liquidity (`NFCI`)**
                4. **Volatility (`^VIX`)**
                5. **Price Trend (`^GSPC`)**

                If **VIX > 35**, the system locks to 100% Crisis.
                """
            )

        st.subheader("Historical Execution Ledger (Last 3 Years Relative to PIT)")
        action_log = pit_backtest[pit_backtest["Action_Triggered"]].copy()
        three_years_ago = pd.Timestamp(resolved_date) - pd.DateOffset(years=3)
        recent_log = action_log[action_log.index >= three_years_ago].copy()
        if recent_log.empty:
            recent_log = action_log.tail(5).copy()

        log_df = pd.merge(
            pit_probs,
            recent_log[["RWRA_Return", "SPY", "QQQ", "TLT", "DBMF", "GLD", "CSHI", "Turnover"]],
            left_index=True,
            right_index=True,
        )
        log_df = log_df.rename(
            columns={
                "SPY": "SPY (S&P 500)",
                "QQQ": "QQQ (Nasdaq 100)",
                "TLT": "TLT (20Y Treasury)",
                "DBMF": "DBMF (Managed Futures)",
                "GLD": "GLD (Gold)",
                "CSHI": "CSHI (High Yield Cash)",
            }
        )
        for col in [
            "Bull",
            "Neutral",
            "Bear",
            "Crisis",
            "SPY (S&P 500)",
            "QQQ (Nasdaq 100)",
            "TLT (20Y Treasury)",
            "DBMF (Managed Futures)",
            "GLD (Gold)",
            "CSHI (High Yield Cash)",
        ]:
            log_df[col] = (log_df[col] * 100).map("{:.1f}%".format)

        log_df["Daily Return"] = (log_df["RWRA_Return"] * 100).map("{:.2f}%".format)
        log_df["Turnover"] = (log_df["Turnover"] * 100).map("{:.1f}%".format)
        log_df = log_df.rename_axis("Date").reset_index()
        log_df["Execution Date"] = log_df["Date"].dt.strftime("%b %d, %Y")

        st.dataframe(
            log_df[
                [
                    "Execution Date",
                    "Bull",
                    "Neutral",
                    "Bear",
                    "Crisis",
                    "SPY (S&P 500)",
                    "QQQ (Nasdaq 100)",
                    "TLT (20Y Treasury)",
                    "DBMF (Managed Futures)",
                    "GLD (Gold)",
                    "CSHI (High Yield Cash)",
                    "Turnover",
                    "Daily Return",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("*Emergency protocol note: if VIX > 35, probabilities lock to 100% Crisis. PIT filtering is UI-only.*")


elif page == "Comparative Strategy Audit":
    st.title("Comparative Strategy Audit")
    st.markdown("Side-by-side performance analysis of all active AI hedging engines versus the 60/40 market benchmark.")

    try:
        from macro_backtest import run_backtest as run_macro
        from rwra_backtest import run_rwra_backtest as run_rwra
    except Exception as exc:
        st.error(f"Failed to import comparison modules. Root cause: {exc}")
        st.stop()

    @st.cache_data(ttl=86400)
    def fetch_comparison_data():
        backtest_macro, _, _, _ = run_macro()
        backtest_rwra, _, _, _, _ = run_rwra()
        return backtest_macro, backtest_rwra

    with st.spinner("Compiling cross-strategy performance data from the local cache..."):
        backtest_macro, backtest_rwra = fetch_comparison_data()

    if backtest_macro is None or backtest_rwra is None or backtest_macro.empty or backtest_rwra.empty:
        st.error("Failed to load strategy metrics for comparison.")
    else:
        common_idx = backtest_macro.index.intersection(backtest_rwra.index).sort_values()
        resolved_date, resolution_reason = resolve_pit_date(common_idx, requested_pit_date)
        pit_macro = backtest_macro.loc[:resolved_date].copy()
        pit_rwra = backtest_rwra.loc[:resolved_date].copy()
        merged_idx = pit_macro.index.intersection(pit_rwra.index).sort_values()
        merged_equity = pd.DataFrame(index=merged_idx)
        merged_equity["RWRA Engine"] = pit_rwra.loc[merged_idx, "Cumulative_Return"]
        merged_equity["Macro Regime"] = pit_macro.loc[merged_idx, "Cumulative_Return"]
        merged_equity["60/40 Benchmark"] = pit_rwra.loc[merged_idx, "60_40_CumRev"]

        metrics_macro = {
            "Strategy": compute_display_metrics(pit_macro["Daily_Return"]),
            "Benchmark": compute_display_metrics(pit_macro["60_40_Ret"]),
        }
        metrics_rwra = {
            "Strategy": compute_display_metrics(pit_rwra["RWRA_Return"]),
            "Benchmark": compute_display_metrics(pit_rwra["60_40_Ret"]),
        }

        render_pit_banner(
            requested_pit_date,
            resolved_date,
            resolution_reason,
            "This comparison table and both charts are truncated at the PIT date.",
        )

        st.subheader("Institutional League Table")
        comp_data = {
            "Metric": ["CAGR (Ann. Return)", "Max Drawdown", "Volatility", "Sharpe Ratio"],
            "RWRA Engine": [
                f"{metrics_rwra['Strategy']['CAGR'] * 100:.1f}%",
                f"{metrics_rwra['Strategy']['Max_DD'] * 100:.1f}%",
                f"{metrics_rwra['Strategy']['Vol'] * 100:.1f}%",
                f"{metrics_rwra['Strategy']['Sharpe']:.2f}",
            ],
            "Macro Regime": [
                f"{metrics_macro['Strategy']['CAGR'] * 100:.1f}%",
                f"{metrics_macro['Strategy']['Max_DD'] * 100:.1f}%",
                f"{metrics_macro['Strategy']['Vol'] * 100:.1f}%",
                f"{metrics_macro['Strategy']['Sharpe']:.2f}",
            ],
            "60/40 Benchmark": [
                f"{metrics_rwra['Benchmark']['CAGR'] * 100:.1f}%",
                f"{metrics_rwra['Benchmark']['Max_DD'] * 100:.1f}%",
                f"{metrics_rwra['Benchmark']['Vol'] * 100:.1f}%",
                f"{metrics_rwra['Benchmark']['Sharpe']:.2f}",
            ],
        }
        st.table(pd.DataFrame(comp_data))

        st.markdown("---")
        st.subheader("Multi-Strategy Cumulative Performance")
        melted_equity = merged_equity.rename_axis("Date").reset_index().melt("Date", var_name="Strategy", value_name="Cumulative Return")
        line_chart = alt.Chart(melted_equity).mark_line(strokeWidth=2).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Cumulative Return:Q", title="Portfolio Value"),
            color=alt.Color(
                "Strategy:N",
                scale=alt.Scale(
                    domain=["RWRA Engine", "Macro Regime", "60/40 Benchmark"],
                    range=["#d2a8ff", "#00f2ff", "#8b949e"],
                ),
            ),
            tooltip=["Date:T", "Strategy:N", alt.Tooltip("Cumulative Return:Q", format=".2f")],
        ).properties(height=400).interactive(bind_y=False)
        st.altair_chart(line_chart, use_container_width=True)

        st.markdown("---")
        st.subheader("Strategy Alpha Persistence")
        st.markdown("*Showing relative outperformance of each strategy versus the 60/40 benchmark through the PIT date.*")
        alpha_df = pd.DataFrame(index=merged_idx)
        alpha_df["RWRA Alpha"] = merged_equity["RWRA Engine"] - merged_equity["60/40 Benchmark"]
        alpha_df["Macro Alpha"] = merged_equity["Macro Regime"] - merged_equity["60/40 Benchmark"]
        melted_alpha = alpha_df.rename_axis("Date").reset_index().melt("Date", var_name="Strategy", value_name="Alpha")
        alpha_chart = alt.Chart(melted_alpha).mark_area(opacity=0.4, line={"color": "white", "strokeWidth": 1}).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Alpha:Q", title="Alpha (vs 60/40)"),
            color=alt.Color(
                "Strategy:N",
                scale=alt.Scale(domain=["RWRA Alpha", "Macro Alpha"], range=["#d2a8ff", "#00f2ff"]),
            ),
            tooltip=["Date:T", "Strategy:N", alt.Tooltip("Alpha:Q", format=".2f")],
        ).properties(height=400).interactive(bind_y=False)
        st.altair_chart(alpha_chart, use_container_width=True)

        st.markdown("---")
        st.subheader("CIO Verdict")
        rwra_sh = metrics_rwra["Strategy"]["Sharpe"]
        macro_sh = metrics_macro["Strategy"]["Sharpe"]
        if rwra_sh > macro_sh:
            st.info("RWRA blending leads on a PIT basis due to stronger risk-adjusted efficiency and lower turnover drag.")
        else:
            st.info("Macro Regime leads on a PIT basis, delivering the stronger return profile through the selected date.")

        st.markdown("*All comparison outputs are filtered at the dashboard layer only. Backend strategy modules are unchanged.*")
