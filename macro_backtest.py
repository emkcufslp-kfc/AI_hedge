import pandas as pd
import numpy as np
import yfinance as yf
import datetime
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings("ignore")

def fetch_macro_data(start_date, end_date):
    """Fetches macro indicators from local FRED cache."""
    try:
        df = pd.read_csv('data/historical_macro.csv', index_col=0, parse_dates=True)
        return df.loc[start_date:end_date]
    except Exception as e:
        print(f"Error loading local FRED cache: {e}")
        return pd.DataFrame()

def fetch_market_data(start_date, end_date):
    """Fetches asset data from local Yahoo Finance cache."""
    try:
        df = pd.read_csv('data/historical_market.csv', index_col=0, parse_dates=True)
        return df.loc[start_date:end_date]
    except Exception as e:
        print(f"Error loading local YF cache: {e}")
        return pd.DataFrame()

def compute_regime_score(macro_df, market_df):
    """
    Computes a simplified 20-point scoring regime using historic data proxies.
    Returns +1 (Bullish), 0 (Neutral), -1 (Bearish) per factor.
    """
    # Merge on date
    df = pd.merge(market_df, macro_df, left_index=True, right_index=True, how='left')
    df = df.ffill().dropna()
    
    scores = pd.DataFrame(index=df.index)
    score_cols = []
    
    # 1-3. Economic (Momentum based on 6M ROC)
    scores['unemp_trend'] = np.where(df['UNRATE'].diff(126) > 0, -1, 1) # ~6 months (126 trading days)
    scores['indpro_trend'] = np.where(df['INDPRO'].pct_change(126) > 0, 1, -1)
    scores['retail_trend'] = np.where(df['RSAFS'].pct_change(126) > 0, 1, -1)
    
    # 4-6. Credit
    scores['hy_spread'] = np.where(df['HY_Spread'] > df['HY_Spread'].rolling(252).mean(), -1, 1)
    scores['bbb_spread'] = np.where(df['BBB_Spread'] > df['BBB_Spread'].rolling(252).mean(), -1, 1)
    scores['stress_idx'] = np.where(df['STLFSI'] > 0, -1, 1) # 0 is absolute neutral threshold for STLFSI
    
    # 7-9. Liquidity
    scores['m2_growth'] = np.where(df['M2'].pct_change(126) > 0.02, 1, -1)
    scores['fed_bs'] = np.where(df['WALCL'].pct_change(60) > 0, 1, -1)
    scores['real_rates'] = np.where(df['Real_Rate'] > df['Real_Rate'].rolling(126).mean(), -1, 1)
    scores['dollar'] = np.where(df['Dollar_Idx'] < df['Dollar_Idx'].rolling(126).mean(), 1, -1)
    
    # 10-12. Market Tech
    scores['sp500_trend'] = np.where(df['^GSPC'] > df['^GSPC'].rolling(200).mean(), 1, -1)
    scores['vix_regime'] = np.where(df['^VIX'] < 20, 1, -1)
    scores['momentum'] = np.where(df['QQQ'].pct_change(60) > df['SPY'].pct_change(60), 1, -1)

    # To reach 20 indicators, we weight the existing structural proxies mathematically 
    # to fit the -20 to +20 range.
    scores['total_score'] = scores.sum(axis=1) * (20/13) # Normalizing base 13 actual factors up to 20 scale 
    
    return scores, df

def assign_regime(score):
    if score > 8: return "STRONG BULL"
    elif score > 3: return "BULL"
    elif score > -3: return "NEUTRAL"
    elif score > -8: return "RISK OFF"
    else: return "CRISIS"

def run_backtest():
    """Main execution entrypoint to run actual historical backtest."""
    end_date = datetime.date.today()
    start_date = end_date - relativedelta(years=20)
    
    macro_data = fetch_macro_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    market_data = fetch_market_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    if macro_data.empty or market_data.empty:
        return None, None
        
    scores, merged_df = compute_regime_score(macro_data, market_data)
    
    # Map regimes dynamically
    scores['Regime'] = scores['total_score'].apply(assign_regime)
    
    # Proxy Allocations based on Regimes (using generic proxy returns)
    merged_df['NTSX_Proxy'] = merged_df['SPY'].pct_change() * 0.9 + merged_df['TLT'].pct_change() * 0.6 
    merged_df['DBMF_Proxy'] = merged_df['SPY'].pct_change() * -0.2 # Rough simplified crisis alpha
    
    merged_df['Ret_QQQ'] = merged_df['QQQ'].pct_change()
    merged_df['Ret_GLD'] = merged_df['GLD'].pct_change()
    merged_df['Ret_SGOV'] = merged_df['SHV'].pct_change() # SHV acting as short duration proxy
    
    portfolio_returns = []
    regimes_used = []
    
    for i in range(1, len(scores)):
        regime = scores['Regime'].iloc[i-1] # Use previous day regime to trade today
        day_rets = merged_df.iloc[i]
        
        if regime == "STRONG BULL":
            ret = (day_rets['NTSX_Proxy']*0.45 + day_rets['Ret_QQQ']*0.25 + day_rets['Ret_QQQ']*0.15 + day_rets['DBMF_Proxy']*0.10 + day_rets['Ret_GLD']*0.05)
        elif regime == "BULL":
            ret = (day_rets['NTSX_Proxy']*0.40 + day_rets['Ret_QQQ']*0.20 + day_rets['Ret_QQQ']*0.15 + day_rets['DBMF_Proxy']*0.15 + day_rets['Ret_GLD']*0.05 + day_rets['Ret_SGOV']*0.05)
        elif regime == "NEUTRAL":
            ret = (day_rets['NTSX_Proxy']*0.30 + day_rets['DBMF_Proxy']*0.20 + day_rets['Ret_GLD']*0.20 + day_rets['Ret_SGOV']*0.30)
        elif regime == "RISK OFF":
            ret = (day_rets['DBMF_Proxy']*0.40 + day_rets['Ret_GLD']*0.30 + day_rets['Ret_SGOV']*0.30)
        else: # CRISIS
            ret = (day_rets['DBMF_Proxy']*0.50 + day_rets['Ret_GLD']*0.30 + day_rets['Ret_SGOV']*0.20)
            
        portfolio_returns.append(ret)
        regimes_used.append(regime)
        
    backtest_df = pd.DataFrame(index=scores.index[1:])
    backtest_df['Daily_Return'] = portfolio_returns
    backtest_df['Regime'] = regimes_used
    backtest_df['Cumulative_Return'] = (1 + backtest_df['Daily_Return']).cumprod()
    
    # 60/40 benchmark
    backtest_df['60_40_Ret'] = merged_df['SPY'].pct_change().iloc[1:] * 0.6 + merged_df['TLT'].pct_change().iloc[1:] * 0.4
    backtest_df['60_40_CumRev'] = (1 + backtest_df['60_40_Ret']).cumprod()
    
    return backtest_df, scores
