import pandas as pd
import yfinance as yf
import datetime
import os

def download_and_save():
    os.makedirs('data', exist_ok=True)
    end_date = datetime.date.today()
    start_date = '2000-01-01'

    # Download Market Data (yfinance)
    print("Downloading Market Data...")
    tickers = ['^GSPC', '^VIX', 'QQQ', 'GLD', 'SPY', 'TLT', 'DBMF', 'CSHI', 'SHV']
    market_df = yf.download(tickers, start=start_date, end=end_date.strftime("%Y-%m-%d"))['Close']
    market_df = market_df.fillna(method='ffill')
    market_df.to_csv('data/historical_market.csv')
    print("Market Data Saved.")

    # Download Macro Data (FRED)
    print("Downloading Macro Data...")
    fred_series = {
        'T10Y2Y': 'T10Y2Y',                # Yield Curve
        'HY_Spread': 'BAMLH0A0HYM2',       # High Yield Spread
        'BBB_Spread': 'BAMLC0A4CBBB',      # BBB Spread
        'Financial_Condition': 'NFCI',     # Fin Conditions
        'UNRATE': 'UNRATE',                # Unemployment
        'INDPRO': 'INDPRO',                # Ind Production
        'RSAFS': 'RSAFS',                  # Retail Sales
        'STLFSI': 'STLFSI4',               # Financial Stress
        'M2': 'M2SL',                      # M2
        'WALCL': 'WALCL',                  # Fed Balance Sheet
        'Real_Rate': 'DFII10',             # 10Y Real Interest Rate
        'Dollar_Idx': 'DTWEXBGS'           # Dollar Index
    }

    import pandas_datareader.data as web
    print("Downloading Macro Data with pandas_datareader...")
    try:
        macro_df = web.DataReader(list(fred_series.values()), 'fred', start_date, end_date.strftime("%Y-%m-%d"))
        macro_df.columns = list(fred_series.keys())
        macro_df = macro_df.fillna(method='ffill')
        macro_df.to_csv('data/historical_macro.csv')
        print("Macro Data Saved.")
    except Exception as e:
        print(f"Failed to download Macro Data: {e}")

if __name__ == "__main__":
    download_and_save()
