import pandas as pd
import numpy as np
import datetime

def run_rwra_backtest():
    try:
        macro_df = pd.read_csv('data/historical_macro.csv', index_col='Date', parse_dates=True)
        market_df = pd.read_csv('data/historical_market.csv', index_col='Date', parse_dates=True)
        
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
    
    # 60/40 Benchmark based on real SPY/TLT
    backtest_df['60_40_Ret'] = asset_rets['SPY'].iloc[1:] * 0.6 + asset_rets['TLT'].iloc[1:] * 0.4
    backtest_df['60_40_CumRev'] = (1 + backtest_df['60_40_Ret']).cumprod()
    
    latest_weights = dict(zip(['SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI'], daily_blended_weights[-1]))
    
    return backtest_df, probs, latest_weights
