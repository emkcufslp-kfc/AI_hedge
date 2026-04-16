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

def compute_metrics(series):
    days = len(series)
    years = days / 252
    cum_ret = (1 + series).prod()
    cagr = (cum_ret ** (1 / years)) - 1 if years > 0 else 0
    vol = series.std() * np.sqrt(252)
    sharpe = cagr / vol if vol > 0 else 0
    
    cumprod_series = (1 + series).cumprod()
    rolling_max = cumprod_series.cummax()
    drawdowns = cumprod_series / rolling_max - 1
    max_dd = drawdowns.min()
    
    return {'CAGR': cagr, 'Vol': vol, 'Sharpe': sharpe, 'Max_DD': max_dd}

def run_backtest():
    """Main execution entrypoint to run actual historical backtest."""
    end_date = datetime.date.today()
    start_date = end_date - relativedelta(years=20)
    
    macro_data = fetch_macro_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    market_data = fetch_market_data(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    if macro_data.empty or market_data.empty:
        return None, None, None
        
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
    action_triggered = []
    daily_turnover = []
    
    weight_map = {
        "STRONG BULL": np.array([0.45, 0.40, 0.10, 0.05, 0.00]),
        "BULL":        np.array([0.40, 0.35, 0.15, 0.05, 0.05]),
        "NEUTRAL":     np.array([0.30, 0.00, 0.20, 0.20, 0.30]),
        "RISK OFF":    np.array([0.00, 0.00, 0.40, 0.30, 0.30]),
        "CRISIS":      np.array([0.00, 0.00, 0.50, 0.30, 0.20])
    }
    
    current_portfolio = np.zeros(5)
    
    for i in range(1, len(scores)):
        regime = scores['Regime'].iloc[i-1] 
        day_rets = merged_df.iloc[i]
        
        target_weights = weight_map.get(regime, np.zeros(5))
        asset_vector = np.array([day_rets['NTSX_Proxy'], day_rets['Ret_QQQ'], day_rets['DBMF_Proxy'], day_rets['Ret_GLD'], day_rets['Ret_SGOV']])
        
        if i == 1:
            current_portfolio = target_weights
            action_triggered.append(True)
            daily_turnover.append(1.0) # 100% turnover on start
            ret = np.dot(current_portfolio, asset_vector)
            
            # Market drift
            current_portfolio = current_portfolio * (1 + asset_vector)
            if np.sum(current_portfolio) > 0:
                current_portfolio = current_portfolio / np.sum(current_portfolio)
        else:
            turnover = np.sum(np.abs(target_weights - current_portfolio))
            
            if turnover > 0.05: # Strict 5% Turnover Threshold
                action_triggered.append(True)
                daily_turnover.append(turnover)
                t_cost = turnover * 0.0010
                current_portfolio = target_weights
            else:
                action_triggered.append(False)
                daily_turnover.append(0.0)
                t_cost = 0 
                
            ret = np.dot(current_portfolio, asset_vector)
            if not np.isnan(t_cost):
                ret -= t_cost
                
            # Post trade market drift
            current_portfolio = current_portfolio * (1 + asset_vector)
            if np.sum(current_portfolio) > 0:
                current_portfolio = current_portfolio / np.sum(current_portfolio)
            
        portfolio_returns.append(ret)
        regimes_used.append(regime)
        
    backtest_df = pd.DataFrame(index=scores.index[1:])
    backtest_df['Daily_Return'] = portfolio_returns
    backtest_df['Action_Triggered'] = action_triggered
    backtest_df['Turnover'] = daily_turnover
    backtest_df['Regime'] = regimes_used
    backtest_df['Cumulative_Return'] = (1 + backtest_df['Daily_Return']).cumprod()
    
    # 60/40 benchmark
    backtest_df['60_40_Ret'] = merged_df['SPY'].pct_change().iloc[1:] * 0.6 + merged_df['TLT'].pct_change().iloc[1:] * 0.4
    backtest_df['60_40_CumRev'] = (1 + backtest_df['60_40_Ret']).cumprod()
    
    metrics = {
        'Strategy': compute_metrics(backtest_df['Daily_Return']),
        'Benchmark': compute_metrics(backtest_df['60_40_Ret'])
    }
    
    latest_prices = merged_df[['QQQ', 'DBMF', 'GLD', 'SHV', 'SPY', 'TLT']].iloc[-1].to_dict()
    
    return backtest_df, scores, metrics, latest_prices
