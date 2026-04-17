$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONPATH = (Join-Path $here ".packages")

@'
from rwra_backtest import run_rwra_backtest

backtest_df, probs, latest_weights, metrics, latest_prices = run_rwra_backtest()
print("Backtest:", metrics["Backtest"])
print("Advisory:", metrics["Advisory"])
print("Latest regime probs:", probs.iloc[-1].to_dict())
print("Target weights:", latest_weights)
'@ | python -
