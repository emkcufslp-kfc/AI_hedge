import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader.data as web
import datetime
from dateutil.relativedelta import relativedelta

def fetch_rwra_data(start_date, end_date):
    """Fetches macro indicators and market data specifically for the RWRA framework."""
    fred_series = {
        'T10Y2Y': 'T10Y2Y',                # Yield Curve
        'HY_Spread': 'BAMLH0A0HYM2',       # Credit Spread
        'Financial_Condition': 'NFCI'      # Financial Conditions / Liquidity (Tight/Loose)
    }
    
    tickers = ['^GSPC', '^VIX', 'QQQ', 'GLD', 'SPY', 'TLT', 'SHV']
    
    try:
        # Fetch FRED
        macro_df = web.DataReader(list(fred_series.values()), 'fred', start_date, end_date)
        macro_df.columns = list(fred_series.keys())
        macro_df = macro_df.fillna(method='ffill')
        
        # Fetch YF
        market_df = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
        market_df = market_df.fillna(method='ffill')
        
        # Merge
        df = pd.merge(market_df, macro_df, left_index=True, right_index=True, how='left')
        df = df.fillna(method='ffill').dropna()
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def compute_rwra_probabilities(df):
    """
    Computes daily probabilities for Bull, Neutral, Bear, Crisis 
    based on the 5 Core Indicators and the VIX > 35 override.
    """
    probs = pd.DataFrame(index=df.index, columns=['Bull', 'Neutral', 'Bear', 'Crisis'])
    
    # Pre-calculate 5 indicators
    yield_curve_inverted = df['T10Y2Y'] < 0
    credit_spread_rising = df['HY_Spread'] > df['HY_Spread'].rolling(252).mean()
    liquidity_tight = df['Financial_Condition'] > 0
    volatility_high = df['^VIX'] > 20
    trend_bearish = df['^GSPC'] < df['^GSPC'].rolling(200).mean()
    
    for i in range(len(df)):
        vix_val = df['^VIX'].iloc[i]
        
        # Emergency Override
        if vix_val > 35:
            probs.iloc[i] = {'Bull': 0.0, 'Neutral': 0.0, 'Bear': 0.0, 'Crisis': 1.0}
            continue
            
        # Count bearish signals (0 to 5)
        bear_score = 0
        if yield_curve_inverted.iloc[i]: bear_score += 1
        if credit_spread_rising.iloc[i]: bear_score += 1
        if liquidity_tight.iloc[i]: bear_score += 1
        if volatility_high.iloc[i]: bear_score += 1
        if trend_bearish.iloc[i]: bear_score += 1
        
        # Simple probabilistic mapping based on bear signals
        if bear_score == 0:
            probs.iloc[i] = {'Bull': 0.70, 'Neutral': 0.20, 'Bear': 0.08, 'Crisis': 0.02}
        elif bear_score == 1:
            probs.iloc[i] = {'Bull': 0.50, 'Neutral': 0.30, 'Bear': 0.15, 'Crisis': 0.05}
        elif bear_score == 2:
            probs.iloc[i] = {'Bull': 0.30, 'Neutral': 0.40, 'Bear': 0.20, 'Crisis': 0.10}
        elif bear_score == 3:
            probs.iloc[i] = {'Bull': 0.10, 'Neutral': 0.35, 'Bear': 0.40, 'Crisis': 0.15}
        elif bear_score == 4:
            probs.iloc[i] = {'Bull': 0.05, 'Neutral': 0.15, 'Bear': 0.50, 'Crisis': 0.30}
        else: # bear_score == 5
            probs.iloc[i] = {'Bull': 0.00, 'Neutral': 0.05, 'Bear': 0.35, 'Crisis': 0.60}
            
    return probs.astype(float)

def run_rwra_backtest():
    end_date = datetime.date.today()
    start_date = end_date - relativedelta(years=20)
    
    df = fetch_rwra_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    if df.empty:
        return None, None, None
        
    probs = compute_rwra_probabilities(df)
    
    # Asset Returns mapping
    # DBMF Proxy (Negative beta to equities during drawdowns, small positive drift otherwise)
    df['DBMF_Proxy'] = np.where(df['SPY'].pct_change() < -0.01, abs(df['SPY'].pct_change()) * 0.8, 0.0001)
    
    asset_rets = pd.DataFrame()
    asset_rets['SPY'] = df['SPY'].pct_change()
    asset_rets['QQQ'] = df['QQQ'].pct_change()
    asset_rets['TLT'] = df['TLT'].pct_change()
    asset_rets['DBMF'] = df['DBMF_Proxy']
    asset_rets['GLD'] = df['GLD'].pct_change()
    asset_rets['CSHI'] = df['SHV'].pct_change() # SHV acting as Cash proxy
    asset_rets = asset_rets.fillna(0)
    
    # Portfolio Weights Matrix per Regime (from Final-Final Upgrade.md)
    weights_bull = np.array([0.40, 0.20, 0.10, 0.10, 0.10, 0.10])
    weights_neutral = np.array([0.25, 0.10, 0.20, 0.20, 0.15, 0.10])
    weights_bear = np.array([0.10, 0.00, 0.25, 0.35, 0.20, 0.10])
    weights_crisis = np.array([0.00, 0.00, 0.30, 0.40, 0.20, 0.10])
    
    portfolio_returns = []
    daily_blended_weights = []
    
    for i in range(1, len(probs)):
        prob_dist = probs.iloc[i-1] # Previous day probability maps to today
        
        # Calculate dynamic blended weight
        blended_weights = (
            prob_dist['Bull'] * weights_bull +
            prob_dist['Neutral'] * weights_neutral +
            prob_dist['Bear'] * weights_bear +
            prob_dist['Crisis'] * weights_crisis
        )
        
        daily_blended_weights.append(blended_weights)
        
        # Multiplied by today's asset returns
        day_ret = np.dot(blended_weights, asset_rets.iloc[i].values)
        portfolio_returns.append(day_ret)
        
    backtest_df = pd.DataFrame(index=probs.index[1:])
    backtest_df['RWRA_Return'] = portfolio_returns
    backtest_df['Cumulative_Return'] = (1 + backtest_df['RWRA_Return']).cumprod()
    
    # Benchmark
    backtest_df['60_40_Ret'] = asset_rets['SPY'].iloc[1:] * 0.6 + asset_rets['TLT'].iloc[1:] * 0.4
    backtest_df['60_40_CumRev'] = (1 + backtest_df['60_40_Ret']).cumprod()
    
    latest_weights = dict(zip(['SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI'], daily_blended_weights[-1]))
    
    return backtest_df, probs, latest_weights
