import pandas as pd
import numpy as np


ASSET_COLUMNS = ['SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI']
REGIMES = ['Bull', 'Neutral', 'Bear', 'Crisis']
INDICATOR_COLUMNS = ['T10Y2Y', 'HY_Spread', 'Financial_Condition', '^VIX', '^GSPC']
PRICE_COLUMNS = ['SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI', 'SHV']


def probability_from_bear_score(bear_score, vix_value):
    """
    Translate the integer bear score into a smooth regime distribution.
    This remains heuristic, but it avoids abrupt jumps caused by hard-coded
    bucket probabilities while preserving a crisis override for severe stress.
    """
    if vix_value > 35:
        return np.array([0.0, 0.0, 0.0, 1.0])

    regime_centers = np.array([0.0, 1.5, 3.5, 5.0])
    distances = np.square(bear_score - regime_centers)
    raw_scores = np.exp(-distances / 1.5)
    return raw_scores / raw_scores.sum()


def default_transition_matrix(p_stay=0.86):
    """
    Persistence-biased transition matrix for the 4 regimes.
    Rows sum to 1.0.
    """
    if not (0.0 < p_stay < 1.0):
        raise ValueError("p_stay must be between 0 and 1")

    t = np.full((4, 4), (1.0 - p_stay) / 3.0, dtype=float)
    np.fill_diagonal(t, p_stay)
    return t


def bayes_filter_probabilities(observed_probs, transition=None, eps=1e-12):
    """
    Treat `observed_probs[t]` as a likelihood vector and run a Bayesian filter.
    """
    if transition is None:
        transition = default_transition_matrix()

    filtered = np.zeros_like(observed_probs, dtype=float)
    prior = np.array([0.25, 0.25, 0.25, 0.25], dtype=float)

    for i in range(observed_probs.shape[0]):
        likelihood = np.maximum(observed_probs[i], eps)
        prior = prior @ transition
        posterior = prior * likelihood
        posterior_sum = posterior.sum()
        if posterior_sum <= 0:
            posterior = np.array([0.25, 0.25, 0.25, 0.25], dtype=float)
        else:
            posterior = posterior / posterior_sum
        filtered[i] = posterior
        prior = posterior

    return filtered


def blend_target_weights(prob_dist):
    weights_bull = np.array([0.40, 0.20, 0.10, 0.10, 0.10, 0.10])
    weights_neutral = np.array([0.25, 0.10, 0.20, 0.20, 0.15, 0.10])
    weights_bear = np.array([0.10, 0.00, 0.25, 0.35, 0.20, 0.10])
    weights_crisis = np.array([0.00, 0.00, 0.30, 0.40, 0.20, 0.10])

    return (
        prob_dist['Bull'] * weights_bull +
        prob_dist['Neutral'] * weights_neutral +
        prob_dist['Bear'] * weights_bear +
        prob_dist['Crisis'] * weights_crisis
    )


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

    observed = np.zeros((len(df), 4), dtype=float)

    for i in range(len(df)):
        vix_val = df['^VIX'].iloc[i]

        # Count bearish signals (0 to 5)
        bear_score = 0
        if yield_curve_inverted.iloc[i]: bear_score += 1
        if credit_spread_rising.iloc[i]: bear_score += 1
        if liquidity_tight.iloc[i]: bear_score += 1
        if volatility_high.iloc[i]: bear_score += 1
        if trend_bearish.iloc[i]: bear_score += 1

        observed[i] = probability_from_bear_score(bear_score, vix_val)

    filtered = bayes_filter_probabilities(observed)
    probs[REGIMES] = filtered

    return probs.astype(float)

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


def build_asset_returns(market_df):
    """
    Build inception-aware daily returns for RWRA assets.
    - DBMF: use live DBMF when available, otherwise a defensive proxy blend.
    - CSHI: use CSHI when available, otherwise SHV as the cash proxy.
    """
    prices = market_df[PRICE_COLUMNS].copy().sort_index().ffill()
    raw_rets = prices.pct_change()

    dbmf_proxy = (
        0.50 * raw_rets['TLT'].fillna(0.0) +
        0.30 * raw_rets['GLD'].fillna(0.0) -
        0.20 * raw_rets['SPY'].fillna(0.0)
    )
    dbmf_live_mask = market_df['DBMF'].notna()
    dbmf_ret = raw_rets['DBMF'].where(dbmf_live_mask, dbmf_proxy)

    cshi_live_mask = market_df['CSHI'].notna()
    cash_ret = raw_rets['CSHI'].where(cshi_live_mask, raw_rets['SHV'])

    asset_rets = pd.DataFrame(index=prices.index)
    asset_rets['SPY'] = raw_rets['SPY']
    asset_rets['QQQ'] = raw_rets['QQQ']
    asset_rets['TLT'] = raw_rets['TLT']
    asset_rets['DBMF'] = dbmf_ret
    asset_rets['GLD'] = raw_rets['GLD']
    asset_rets['CSHI'] = cash_ret
    return asset_rets.fillna(0.0)


def run_rwra_backtest(lookback_years=10):
    try:
        macro_df = pd.read_csv('data/historical_macro.csv', index_col=0, parse_dates=True)
        market_df = pd.read_csv('data/historical_market.csv', index_col=0, parse_dates=True)

        merged = pd.merge(market_df, macro_df, left_index=True, right_index=True, how='left').sort_index()
    except Exception as e:
        print(f"Error loading cached data: {e}")
        return None, None, None, None, None

    if merged.empty:
        return None, None, None, None, None

    regime_source = merged[INDICATOR_COLUMNS].copy().ffill().dropna()
    if regime_source.empty:
        return None, None, None, None, None

    probs_full = compute_rwra_probabilities(regime_source)
    asset_rets_full = build_asset_returns(market_df)

    end_date = min(probs_full.index.max(), asset_rets_full.index.max())
    start_date = end_date - pd.DateOffset(years=lookback_years)

    common_idx = probs_full.index.intersection(asset_rets_full.index)
    common_idx = common_idx[(common_idx >= start_date) & (common_idx <= end_date)]
    if len(common_idx) < 2:
        return None, None, None, None, None

    probs = probs_full.loc[common_idx]
    asset_rets = asset_rets_full.loc[common_idx]
    
    portfolio_returns = []
    target_weight_history = []
    action_triggered = []
    daily_turnover = []
    
    current_portfolio = np.zeros(6)
    last_executed_probs = None
    
    for i in range(1, len(probs)):
        prob_dist = probs.iloc[i-1]
        target_weights = blend_target_weights(prob_dist)
        
        day_rets = asset_rets.iloc[i].values
        
        if i == 1:
            current_portfolio = target_weights
            action_triggered.append(True)
            daily_turnover.append(1.0) # Initial entry is 100% turnover
            day_ret = np.dot(current_portfolio, day_rets)
            last_executed_probs = prob_dist.copy()
            
            # Market drift
            current_portfolio = current_portfolio * (1 + day_rets)
            if np.sum(current_portfolio) > 0:
                current_portfolio = current_portfolio / np.sum(current_portfolio)
        else:
            turnover_delta = np.sum(np.abs(target_weights - current_portfolio))
            prob_shift = 0.0
            if last_executed_probs is not None:
                prob_shift = float(np.sum(np.abs(prob_dist.values - last_executed_probs.values)))

            should_rebalance = (turnover_delta > 0.05) or (prob_shift > 0.50) or (float(prob_dist['Crisis']) > 0.60)
            
            if should_rebalance:
                action_triggered.append(True)
                daily_turnover.append(turnover_delta)
                t_cost = turnover_delta * 0.0010
                current_portfolio = target_weights
                last_executed_probs = prob_dist.copy()
            else:
                action_triggered.append(False)
                daily_turnover.append(0.0)
                t_cost = 0 
                
            day_ret = np.dot(current_portfolio, day_rets) - t_cost
            
            current_portfolio = current_portfolio * (1 + day_rets)
            if np.sum(current_portfolio) > 0:
                current_portfolio = current_portfolio / np.sum(current_portfolio)
                
        target_weight_history.append(target_weights.copy())
        portfolio_returns.append(day_ret)
        
    backtest_df = pd.DataFrame(index=probs.index[1:])
    backtest_df['RWRA_Return'] = portfolio_returns
    backtest_df['Action_Triggered'] = action_triggered
    backtest_df['Turnover'] = daily_turnover
    backtest_df['Cumulative_Return'] = (1 + backtest_df['RWRA_Return']).cumprod()
    
    # Persist target execution weights instead of post-drift holdings.
    weights_df = pd.DataFrame(target_weight_history, index=probs.index[1:], columns=ASSET_COLUMNS)
    backtest_df = pd.concat([backtest_df, weights_df], axis=1)
    
    # 60/40 Benchmark based on real SPY/TLT
    backtest_df['60_40_Ret'] = asset_rets['SPY'].iloc[1:] * 0.6 + asset_rets['TLT'].iloc[1:] * 0.4
    backtest_df['60_40_CumRev'] = (1 + backtest_df['60_40_Ret']).cumprod()
    
    latest_target_weights = blend_target_weights(probs.iloc[-1])
    latest_weights = dict(zip(ASSET_COLUMNS, latest_target_weights))
    turnover_to_target = float(np.sum(np.abs(latest_target_weights - current_portfolio)))
    prob_shift_to_last_exec = 0.0
    if last_executed_probs is not None:
        prob_shift_to_last_exec = float(np.sum(np.abs(probs.iloc[-1].values - last_executed_probs.values)))
    
    metrics = {
        'Strategy': compute_metrics(backtest_df['RWRA_Return']),
        'Benchmark': compute_metrics(backtest_df['60_40_Ret']),
        'Backtest': {
            'Start_Date': backtest_df.index.min().strftime('%Y-%m-%d'),
            'End_Date': backtest_df.index.max().strftime('%Y-%m-%d'),
            'Lookback_Years': lookback_years
        },
        'Advisory': {
            'Action_Needed': (turnover_to_target > 0.05) or (prob_shift_to_last_exec > 0.50) or (float(probs.iloc[-1]['Crisis']) > 0.60),
            'Turnover_To_Target': turnover_to_target,
            'Prob_Shift_To_Last_Exec': prob_shift_to_last_exec,
            'Crisis_Prob': float(probs.iloc[-1]['Crisis'])
        }
    }
    
    latest_price_source = market_df[PRICE_COLUMNS].sort_index().ffill().loc[:end_date]
    latest_price_row = latest_price_source.iloc[-1]
    latest_prices = {
        'SPY': float(latest_price_row['SPY']),
        'QQQ': float(latest_price_row['QQQ']),
        'TLT': float(latest_price_row['TLT']),
        'DBMF': float(latest_price_row['DBMF']) if pd.notna(latest_price_row['DBMF']) else float(latest_price_row['GLD']),
        'GLD': float(latest_price_row['GLD']),
        'CSHI': float(latest_price_row['CSHI']) if pd.notna(latest_price_row['CSHI']) else float(latest_price_row['SHV'])
    }
    
    return backtest_df, probs, latest_weights, metrics, latest_prices
