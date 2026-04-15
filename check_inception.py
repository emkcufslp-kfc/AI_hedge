import yfinance as yf

for t in ['SPY', 'QQQ', 'TLT', 'DBMF', 'GLD', 'CSHI', 'SHV']:
    ticker = yf.Ticker(t)
    df = ticker.history(period="max")
    if not df.empty:
        print(f"{t}: {df.index.min().date()}")
    else:
        print(f"{t}: Data missing")
