#!/usr/bin/env python3
"""
Fetch ~3 years of daily OHLCV for the Pyodide playground's stock-demo
whitelist and write parallel-array JSON snapshots into the website-resources
working tree.

Output:
    docs/clone_website_resources/imgui-bundle.pages.dev/stock_data/<slug>.json
where <slug> is the ticker with "." replaced by "_" (e.g. MC.PA -> MC_PA).

The output lives in a separately-tracked repo (imgui_bundle_website_resources).
After running this script, commit + push that working tree by hand.

Usage:
    just cf_fetch_stock_data                  # recommended
    python ci_scripts/cf_fetch_stock_data.py  # direct
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import yfinance as yf  # type: ignore[import-untyped]


# Whitelist locked in _plans/stock_demo_revamp__spec.md.
TICKERS: dict[str, str] = {
    "AAPL":    "USD",
    "MSFT":    "USD",
    "GOOGL":   "USD",
    "NVDA":    "USD",
    "MC.PA":   "EUR",  # LVMH
    "OR.PA":   "EUR",  # L'Oréal
    "AIR.PA":  "EUR",  # Airbus
    "DSY.PA":  "EUR",  # Dassault Systèmes
    "ASML.AS": "EUR",  # ASML (Euronext Amsterdam)
}

PERIOD = "3y"
INTERVAL = "1d"

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = (
    REPO_ROOT
    / "docs" / "clone_website_resources" / "imgui-bundle.pages.dev" / "stock_data"
)


def fetch_one(ticker: str, currency: str) -> dict[str, Any]:
    df = yf.download(
        ticker, period=PERIOD, interval=INTERVAL,
        auto_adjust=False, progress=False,
    )
    if df is None or df.empty:
        raise RuntimeError("no data returned")
    df = df.dropna()
    ts = [int(t.timestamp()) for t in df.index]
    opens = np.round(df["Open"].to_numpy().flatten(), 2).tolist()
    highs = np.round(df["High"].to_numpy().flatten(), 2).tolist()
    lows = np.round(df["Low"].to_numpy().flatten(), 2).tolist()
    closes = np.round(df["Close"].to_numpy().flatten(), 2).tolist()
    volumes = df["Volume"].to_numpy().astype(np.int64).flatten().tolist()
    slug = ticker.replace(".", "_")
    return {
        "ticker": ticker,
        "slug": slug,
        "currency": currency,
        "interval": INTERVAL,
        "fetched_at": date.today().isoformat(),
        "ts": ts,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }


def main() -> int:
    if not OUTPUT_DIR.parent.exists():
        print(
            f"ERROR: {OUTPUT_DIR.parent} does not exist.\n"
            f"       Run `just cf_resources_sync` first to clone the "
            f"website-resources repo.",
            file=sys.stderr,
        )
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    for ticker, currency in TICKERS.items():
        try:
            doc = fetch_one(ticker, currency)
        except Exception as e:
            print(f"  FAIL  {ticker}: {e}", file=sys.stderr)
            failures.append(ticker)
            continue
        out = OUTPUT_DIR / f"{doc['slug']}.json"
        with out.open("w") as f:
            json.dump(doc, f, separators=(",", ":"))
        n = len(doc["ts"])
        kb = out.stat().st_size / 1024
        print(
            f"  OK    {ticker:8s} ({currency})  {n:4d} rows  {kb:5.1f} KB  "
            f"-> {out.relative_to(REPO_ROOT)}"
        )

    if failures:
        print(
            f"\n{len(failures)} ticker(s) failed: {', '.join(failures)}",
            file=sys.stderr,
        )
        return 2
    print(f"\nWrote {len(TICKERS)} files to {OUTPUT_DIR.relative_to(REPO_ROOT)}")
    print(
        "Remember to commit + push from docs/clone_website_resources/ "
        "(separate repo)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
