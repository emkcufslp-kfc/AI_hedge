import pandas as pd
import numpy as np

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
    try:
        macro_df = pd.read_csv('data/historical_macro.csv', index_col=0, parse_dates=True)
        market_df = pd.read_csv('data/historical_market.csv', index_col=0, parse_dates=True)
        
        df = pd.merge(market_df, macro_df, left_index=True, right_index=True, how='left')
        df = df.dropna()
    except Exception as e:
        print(f"Error loading cached data: {e}")
        return None, None, None

    if df.empty:
        return None, None, None
        
    probs = compute_rwra_probabilities(df)
    
    asset_rets = pd.DataFrame()
    asset_rets['SPY'] = df['SPY'].pct_change()
    asset_rets['QQQ'] = df['QQQ'].pct_change()
    asset_rets['TLT'] = df['TLT'].pct_change()
    asset_rets['DBMF'] = df['DBMF'].pct_change()
    asset_rets['GLD'] = df['GLD'].pct_change()
    asset_rets['CSHI'] = df['CSHI'].pct_change() 
    asset_rets = asset_rets.fillna(0)
    
    # Portfolio Weights Matrix per Regime
    weights_bull = np.array([0.40, 0.20, 0.10, 0.10, 0.10, 0.10])
    weights_neutral = np.array([0.25, 0.10, 0.20, 0.20, 0.15, 0.10])
    weights_bear = np.array([0.10, 0.00, 0.25, 0.35, 0.20, 0.10])
    weights_crisis = np.array([0.00, 0.00, 0.30, 0.40, 0.20, 0.10])
    
    portfolio_returns = []
    daily_blended_weights = []
    
    for i in range(1, len(probs)):
        prob_dist = probs.iloc[i-1] 
        
        blended_weights = (
            prob_dist['Bull'] * weights_bull +
            prob_dist['Neutral'] * weights_neutral +
            prob_dist['Bear'] * weights_bear +
            prob_dist['Crisis'] * weights_crisis
        )
        
        daily_blended_weights.append(blended_weights)
        day_ret = np.dot(blended_weights, asset_rets.iloc[i].values)
        portfolio_returns.append(day_ret)
        
    backtest_df = pd.DataFrame(index=probs.index[1:])
    backtest_df['RWRA_Return'] = portfolio_returns
    backtest_df['Cumulative_Return'] = (1 + backtest_df['RWRA_Return']).cumprod()
    
    # Attach the weights matrix to backtest_df for transaction logging
    weights_df = pd.DataFrame(daily_blended_weights, index=probs.index[1:], columns=['SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI'])
    backtest_df = pd.concat([backtest_df, weights_df], axis=1)
    
    # 60/40 Benchmark based on real SPY/TLT
    backtest_df['60_40_Ret'] = asset_rets['SPY'].iloc[1:] * 0.6 + asset_rets['TLT'].iloc[1:] * 0.4
    backtest_df['60_40_CumRev'] = (1 + backtest_df['60_40_Ret']).cumprod()
    
    latest_weights = dict(zip(['SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI'], daily_blended_weights[-1]))
    
    return backtest_df, probs, latest_weights
