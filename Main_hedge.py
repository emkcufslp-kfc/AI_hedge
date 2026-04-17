from rwra_backtest import run_rwra_backtest


def format_weights(weights):
    ordered_assets = ["SPY", "QQQ", "TLT", "DBMF", "GLD", "CSHI"]
    return "\n".join(f"  - {asset}: {weights[asset] * 100:.1f}%" for asset in ordered_assets)


def main():
    backtest_df, probs, latest_weights, metrics, latest_prices = run_rwra_backtest()
    if backtest_df is None or backtest_df.empty:
        print("RWRA backtest failed. Install dependencies and verify cached data files are present.")
        return

    advisory = metrics.get("Advisory", {})
    backtest_meta = metrics.get("Backtest", {})
    latest_probs = probs.iloc[-1]

    print("AI Hedge - RWRA Recommendation")
    print("=" * 32)
    print(f"Sample window: {backtest_meta.get('Start_Date', 'n/a')} to {backtest_meta.get('End_Date', 'n/a')}")
    print(
        "Action: "
        + ("REBALANCE" if advisory.get("Action_Needed") else "HOLD")
        + f" (turnover to target: {advisory.get('Turnover_To_Target', 0.0) * 100:.1f}%)"
    )
    print(
        "Regime probabilities: "
        f"Bull {latest_probs['Bull'] * 100:.1f}%, "
        f"Neutral {latest_probs['Neutral'] * 100:.1f}%, "
        f"Bear {latest_probs['Bear'] * 100:.1f}%, "
        f"Crisis {latest_probs['Crisis'] * 100:.1f}%"
    )
    print("Target weights:")
    print(format_weights(latest_weights))
    print(
        "Backtest metrics: "
        f"CAGR {metrics['Strategy']['CAGR'] * 100:.1f}%, "
        f"MaxDD {metrics['Strategy']['Max_DD'] * 100:.1f}%, "
        f"Sharpe {metrics['Strategy']['Sharpe']:.2f}"
    )
    print(
        "Latest prices: "
        + ", ".join(f"{ticker} ${price:.2f}" for ticker, price in latest_prices.items())
    )


if __name__ == "__main__":
    main()
