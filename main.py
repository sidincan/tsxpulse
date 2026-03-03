from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timezone
import time
import pytz
import anthropic
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── UNIVERSE ──────────────────────────────────────────────────────────────────
# Delisted/acquired removed: PXD (→XOM), HES (→CVX), SSL, BPF, TRIL, CATO,
# PRYM, BUZZ, DNLI, EMP, SCI, INE, BEP, FOR, ADW

TSX_UNIVERSE = [
    # Financials
    {"ticker":"RY",   "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"TD",   "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"BNS",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"BMO",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"CM",   "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"MFC",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"SLF",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"FFH",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"IFC",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"GWO",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"POW",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"IAG",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"EQB",  "market":"TSX","currency":"CAD","sector":"Financials"},
    {"ticker":"CWB",  "market":"TSX","currency":"CAD","sector":"Financials"},
    # Energy
    {"ticker":"CNQ",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"SU",   "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"CVE",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"TOU",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"WCP",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"ARX",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"BTE",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"ERF",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"POU",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"PSK",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"TPZ",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"PEY",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"MEG",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"VET",  "market":"TSX","currency":"CAD","sector":"Energy"},
    {"ticker":"GEI",  "market":"TSX","currency":"CAD","sector":"Energy"},
    # Materials
    {"ticker":"ABX",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"WPM",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"FM",   "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"AGI",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"AEM",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"K",    "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"IMG",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"LUN",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"CS",   "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"OR",   "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"CIA",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"WDO",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"EDV",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"DPM",  "market":"TSX","currency":"CAD","sector":"Materials"},
    # Technology
    {"ticker":"SHOP", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"CSU",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"ENGH", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"KXS",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"DCBO", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"LSPD", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"TOI",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"DSGX", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"OTEX", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"GIB",  "market":"TSX","currency":"CAD","sector":"Technology"},
    # Industrials
    {"ticker":"CP",   "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"CN",   "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"CAE",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TRI",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"WSP",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"STN",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"BYD",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"GFL",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"WCN",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TFII", "market":"TSX","currency":"CAD","sector":"Industrials"},
    # Consumer
    {"ticker":"MRU",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"L",    "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"DOL",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"ATD",  "market":"TSX","currency":"CAD","sector":"Consumer"},  # FIX #3: removed duplicate ATD
    {"ticker":"QSR",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"MTY",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"GIL",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"CTC",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    # Utilities
    {"ticker":"FTS",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"AQN",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"H",    "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"NPI",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"CPX",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"EMA",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"ALA",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"CU",   "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"PPL",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"KEY",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"TA",   "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"BLX",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    # Healthcare
    {"ticker":"NVO",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"CLS",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"WELL", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"GUD",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"DND",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"HLS",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"PBH",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"CURA", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"VHI",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
]

US_UNIVERSE = [
    # Technology
    {"ticker":"AAPL", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"MSFT", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"NVDA", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"AMZN", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"GOOGL","market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"META", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"TSLA", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"AMD",  "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"ORCL", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"CRM",  "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"ADBE", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"NOW",  "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"INTC", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"QCOM", "market":"NYSE","currency":"USD","sector":"Technology"},
    {"ticker":"AMAT", "market":"NYSE","currency":"USD","sector":"Technology"},
    # Financials
    {"ticker":"JPM",  "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"BAC",  "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"GS",   "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"MS",   "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"V",    "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"MA",   "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"BRK-B","market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"WFC",  "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"C",    "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"AXP",  "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"BLK",  "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"SCHW", "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"CB",   "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"PGR",  "market":"NYSE","currency":"USD","sector":"Financials"},
    {"ticker":"AON",  "market":"NYSE","currency":"USD","sector":"Financials"},
    # Healthcare
    {"ticker":"JNJ",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"UNH",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"LLY",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"ABBV", "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"MRK",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"TMO",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"ABT",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"DHR",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"PFE",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"AMGN", "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"GILD", "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"ISRG", "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"BSX",  "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"REGN", "market":"NYSE","currency":"USD","sector":"Healthcare"},
    {"ticker":"VRTX", "market":"NYSE","currency":"USD","sector":"Healthcare"},
    # Energy
    {"ticker":"XOM",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"CVX",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"COP",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"EOG",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"SLB",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"MPC",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"PSX",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"VLO",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"HAL",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"DVN",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"OXY",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"BKR",  "market":"NYSE","currency":"USD","sector":"Energy"},
    # Consumer
    {"ticker":"WMT",  "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"COST", "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"MCD",  "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"SBUX", "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"NKE",  "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"HD",   "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"LOW",  "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"TGT",  "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"PG",   "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"KO",   "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"PEP",  "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"PM",   "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"CL",   "market":"NYSE","currency":"USD","sector":"Consumer"},
    {"ticker":"MDLZ", "market":"NYSE","currency":"USD","sector":"Consumer"},
    # Industrials
    {"ticker":"CAT",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"DE",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"HON",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"UPS",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"RTX",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"LMT",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"GE",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"BA",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"FDX",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"EMR",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"ETN",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"GD",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"NOC",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    # Materials
    {"ticker":"LIN",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"APD",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"SHW",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"ECL",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"NEM",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"FCX",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"NUE",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"VMC",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"DOW",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"DD",   "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"ALB",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"CF",   "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"MOS",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"AA",   "market":"NYSE","currency":"USD","sector":"Materials"},
    # Utilities
    {"ticker":"NEE",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"DUK",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"SO",   "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"D",    "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"AEP",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"EXC",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"XEL",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"ED",   "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"ETR",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"FE",   "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"EIX",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"ES",   "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"AWK",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    {"ticker":"WEC",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    # ETFs
    {"ticker":"SPY",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"QQQ",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"GLD",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLF",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLE",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLV",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLK",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLI",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLB",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLU",  "market":"NYSE","currency":"USD","sector":"ETF"},
]

# Deduplicate
def dedup(lst):
    seen = set()
    out = []
    for s in lst:
        if s["ticker"] not in seen:
            seen.add(s["ticker"])
            out.append(s)
    return out

TSX_UNIVERSE  = dedup(TSX_UNIVERSE)
US_UNIVERSE   = dedup(US_UNIVERSE)
FULL_UNIVERSE = dedup(TSX_UNIVERSE + US_UNIVERSE)


# ── DATA DOWNLOAD — SEQUENTIAL, ONE STOCK AT A TIME ──────────────────────────

def download_single(yf_ticker: str) -> pd.DataFrame:
    """
    Downloads one stock sequentially. Retries once with 3s backoff on
    rate limit or empty response.
    """
    for attempt in range(2):
        try:
            df = yf.download(
                yf_ticker,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True,
                group_by="ticker"
            )
            if df is None or df.empty:
                if attempt == 0:
                    time.sleep(3)
                    continue
                return pd.DataFrame()

            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                level_0 = [str(v) for v in df.columns.get_level_values(0)]
                level_1 = [str(v) for v in df.columns.get_level_values(1)]
                if "Close" in level_0:
                    df.columns = df.columns.droplevel(1)
                elif "Close" in level_1:
                    df.columns = df.columns.droplevel(0)
                else:
                    df.columns = [str(c[0]) for c in df.columns]

            df.columns = [str(c) for c in df.columns]

            if "Close" not in df.columns:
                if attempt == 0:
                    time.sleep(3)
                    continue
                return pd.DataFrame()

            df = df[~df.index.duplicated(keep="last")]
            df = df.dropna(subset=["Close", "High", "Low", "Volume"])
            return df

        except Exception as e:
            print(f"Download error {yf_ticker} (attempt {attempt+1}): {e}")
            if attempt == 0:
                time.sleep(3)
                continue
            return pd.DataFrame()

    return pd.DataFrame()


# ── EARNINGS FILTER ───────────────────────────────────────────────────────────

def is_near_earnings(ticker: str, market: str, days_buffer: int = 5) -> dict:
    try:
        yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker
        stock = yf.Ticker(yf_ticker)
        cal = stock.calendar
        if cal is None or cal.empty:
            return {"near_earnings": False, "earnings_date": None}
        if "Earnings Date" in cal.index:
            earnings_date = pd.to_datetime(cal.loc["Earnings Date"].iloc[0])
        elif "Earnings Date" in cal.columns:
            earnings_date = pd.to_datetime(cal["Earnings Date"].iloc[0])
        else:
            return {"near_earnings": False, "earnings_date": None}
        today = pd.Timestamp.now().normalize()
        days_to = (earnings_date - today).days
        return {
            "near_earnings": 0 <= days_to <= days_buffer,
            "earnings_date": earnings_date.strftime("%Y-%m-%d"),
            "days_to_earnings": int(days_to)
        }
    except Exception:
        return {"near_earnings": False, "earnings_date": None}


# ── SIGNAL COMPUTATION ────────────────────────────────────────────────────────

def compute_signal(stock: dict, idx: int = 0, total: int = 0) -> dict:
    ticker   = stock["ticker"]
    market   = stock["market"]
    currency = stock["currency"]
    sector   = stock.get("sector", "")
    yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker

    try:
        df = download_single(yf_ticker)

        if len(df) < 200:
            print(f"SKIP {ticker} ({idx}/{total}): only {len(df)} rows")
            return None

        close  = df["Close"].squeeze()
        volume = df["Volume"].squeeze()
        high   = df["High"].squeeze()
        low    = df["Low"].squeeze()

        for name, s in [("close", close), ("volume", volume), ("high", high), ("low", low)]:
            if not isinstance(s, pd.Series):
                print(f"SKIP {ticker} ({idx}/{total}): {name} is not 1D")
                return None

        # Signal 1: MACD Momentum
        macd_ind = ta.trend.MACD(close, window_slow=21, window_fast=9, window_sign=9)
        hist     = macd_ind.macd_diff()
        tm_score = 1 if (hist.iloc[-1] > 0 and hist.iloc[-1] > hist.iloc[-2]) else 0

        # Signal 2: RSI + SMA
        rsi_val       = float(ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1])
        sma50         = close.rolling(50).mean()
        sma200        = close.rolling(200).mean()
        current_price = float(close.iloc[-1])

        # Price sanity: current price must be within 20% of 20-day median
        recent_median = float(close.iloc[-20:].median())
        if current_price < recent_median * 0.80 or current_price > recent_median * 1.20:
            print(f"PRICE OUTLIER {ticker} ({idx}/{total}): current=${current_price:.2f} vs 20d median=${recent_median:.2f} — skipping")
            return None

        # FIX #2: compute above_200 here so it can be returned in the dict
        above_200 = current_price > float(sma200.iloc[-1])

        pq_score = 1 if (40 <= rsi_val <= 60 and current_price > float(sma50.iloc[-1])) else 0

        # Signal 3: Volume + OBV
        vol_ratio = float(volume.iloc[-1] / volume.rolling(20).mean().iloc[-1])
        obv       = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
        obv_slope = float(obv.iloc[-1] - obv.iloc[-6])
        vc_score  = 1 if (vol_ratio < 0.8 and obv_slope > 0) else 0

        # ATR
        atr = float(ta.volatility.AverageTrueRange(
            high, low, close, window=14).average_true_range().iloc[-1])

        # ADX
        adx_val   = float(ta.trend.ADXIndicator(high, low, close, window=14).adx().iloc[-1])
        adx_score = 1 if adx_val >= 20 else 0

        # CMS base (4 components)
        cms_base = round((tm_score * 0.35) + (pq_score * 0.25) + (vc_score * 0.15) + (adx_score * 0.15), 3)
        confirm  = current_price > float(close.iloc[-2])

        # IMS — last 30 min of previous session (3:30–4:00 PM ET)
        # Weight: 20% of final CMS — narrowed window captures institutional final positioning
        ims_score  = 0.5  # neutral default
        ims_trend  = "NEUTRAL"
        ims_detail = {}
        if cms_base >= 0.55:
            try:
                et = pytz.timezone("America/New_York")
                raw_intra = yf.download(
                    yf_ticker, period="2d", interval="5m",
                    progress=False, auto_adjust=True
                )
                if not raw_intra.empty:
                    if isinstance(raw_intra.columns, pd.MultiIndex):
                        raw_intra.columns = raw_intra.columns.get_level_values(0)
                    if raw_intra.index.tz is None:
                        raw_intra.index = raw_intra.index.tz_localize("UTC").tz_convert(et)
                    else:
                        raw_intra.index = raw_intra.index.tz_convert(et)
                    now_et    = datetime.now(et)
                    today_str = now_et.strftime("%Y-%m-%d")
                    all_dates  = sorted(set(raw_intra.index.strftime("%Y-%m-%d")))
                    prev_dates = [d for d in all_dates if d < today_str]
                    if prev_dates:
                        prev_date = prev_dates[-1]
                        day_df    = raw_intra[raw_intra.index.strftime("%Y-%m-%d") == prev_date]
                        # Last 30 min: 3:30–4:00 PM ET
                        last90 = day_df[(day_df.index.hour > 15) |
                                        ((day_df.index.hour == 15) & (day_df.index.minute >= 30))]
                        if len(last90) >= 2:
                            c = last90["Close"].squeeze().astype(float)
                            v = last90["Volume"].squeeze().astype(float)
                            o = last90["Open"].squeeze().astype(float)
                            h = last90["High"].squeeze().astype(float)
                            l = last90["Low"].squeeze().astype(float)
                            typical  = (h + l + c) / 3
                            vwap_val = float((typical * v).cumsum().iloc[-1] / v.cumsum().iloc[-1])
                            price_chg = (float(c.iloc[-1]) - float(c.iloc[0])) / float(c.iloc[0]) * 100
                            mid = max(1, len(v) // 2)
                            vol_trend_up = float(v.iloc[mid:].mean()) > float(v.iloc[:mid].mean()) * 1.1
                            rng       = float(h.max()) - float(l.min())
                            close_str = round((float(c.iloc[-1]) - float(l.min())) / rng * 100, 1) if rng > 0 else 50
                            above_vwap = float(c.iloc[-1]) > vwap_val
                            green_c   = int(((c - o) > 0).sum())
                            red_c     = int(((c - o) < 0).sum())
                            ims_score = 0.0
                            if price_chg > 0:    ims_score += 0.30
                            if vol_trend_up:      ims_score += 0.25
                            if close_str >= 60:   ims_score += 0.25
                            if above_vwap:        ims_score += 0.10
                            if green_c > red_c:   ims_score += 0.10
                            ims_score = round(ims_score, 2)
                            ims_trend = "STRONG_CLOSE" if ims_score >= 0.65 else \
                                        "WEAK_CLOSE"   if ims_score <= 0.30 else "NEUTRAL"
                            ims_detail = {
                                "price_chg_pct":  round(price_chg, 2),
                                "close_strength": close_str,
                                "above_vwap":     above_vwap,
                                "vol_trend":      "increasing" if vol_trend_up else "steady/falling",
                                "green_candles":  green_c,
                                "red_candles":    red_c,
                                "vwap":           round(vwap_val, 2)
                            }
            except Exception as ims_e:
                print(f"IMS fetch error for {ticker}: {ims_e}")

        # Final CMS: 4 base components (80%) + IMS (20%)
        cms = round(cms_base * 0.80 + ims_score * 0.20, 3)

        earnings_info = {"near_earnings": False, "earnings_date": None}
        if cms >= 0.60:
            earnings_info = is_near_earnings(ticker, market)

        entry_signal = (
            cms >= 0.80
            and above_200
            and confirm
            and rsi_val < 70
            and adx_val >= 20
            and not earnings_info["near_earnings"]
        )

        # ── PRE-MARKET GAP FILTER ─────────────────────────────────────────────
        # Detect overnight gap >3% down before flagging as entry.
        # Prevents ABBV/AA-style false signals from overnight gap-downs.
        gap_risk     = False
        gap_pct      = None
        premarket_px = None
        if entry_signal:
            try:
                pm_data = yf.download(
                    yf_ticker, period="1d", interval="1m",
                    progress=False, auto_adjust=True, prepost=True
                )
                if not pm_data.empty:
                    if isinstance(pm_data.columns, pd.MultiIndex):
                        pm_data.columns = pm_data.columns.get_level_values(0)
                    if "Close" in pm_data.columns:
                        pm_close     = float(pm_data["Close"].dropna().iloc[-1])
                        premarket_px = round(pm_close, 2)
                        raw_gap      = (pm_close - current_price) / current_price * 100
                        gap_pct      = round(raw_gap, 2)
                        if raw_gap < -3.0:
                            gap_risk     = True
                            entry_signal = False
                            print(f"GAP RISK {ticker}: scan=${current_price:.2f} pm=${pm_close:.2f} gap={gap_pct}%")
            except Exception as gp_e:
                print(f"Pre-market gap check skipped for {ticker}: {gp_e}")

        stop = round(max(current_price - 2.0 * atr, current_price * 0.93), 2)

        print(f"OK {ticker} ({idx}/{total}) price=${current_price:.2f} CMS={cms}")

        return {
            "ticker":           ticker,
            "market":           market,
            "currency":         currency,
            "sector":           sector,
            "price":            round(current_price, 2),
            "cms":              cms,
            "rsi":              round(rsi_val, 2),
            "tm_score":         tm_score,
            "pq_score":         pq_score,
            "vc_score":         vc_score,
            "adx":              round(adx_val, 2),
            "adx_score":        adx_score,
            "above_200":        above_200,           # FIX #2: now included in return dict
            "entry_signal":     entry_signal,
            "gap_risk":         gap_risk,
            "gap_pct":          gap_pct,
            "premarket_px":     premarket_px,
            "earnings_blocked": earnings_info["near_earnings"],
            "earnings_date":    earnings_info.get("earnings_date"),
            "days_to_earnings": earnings_info.get("days_to_earnings"),
            "ims_score":        ims_score,
            "ims_trend":        ims_trend,
            "ims_detail":       ims_detail,
            "stop":             stop,
            "target_1":         round(current_price * 1.08, 2),
            "target_2":         round(current_price * 1.15, 2),
            "signal_strength":  "STRONG" if cms >= 0.80 else "MODERATE" if cms >= 0.60 else "WEAK",
            "timestamp":        datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error computing {ticker} ({idx}/{total}): {e}")
        return None


# ── SEQUENTIAL SCAN ───────────────────────────────────────────────────────────

def sequential_scan(universe: list) -> list:
    results = []
    total   = len(universe)
    for idx, stock in enumerate(universe, 1):
        result = compute_signal(stock, idx, total)
        if result:
            results.append(result)
        time.sleep(0.3)
    print(f"Scan complete: {len(results)}/{total} stocks processed")
    return sorted(results, key=lambda x: x["cms"], reverse=True)


# ── ROUTES ────────────────────────────────────────────────────────────────────

# FIX #1: Removed duplicate /health stub that was here.
# Single /health endpoint is defined at the bottom with full universe counts.

@app.get("/rescore/{ticker}")
def rescore_ticker(ticker: str, market: str = "TSX"):
    """Re-score a single tracked ticker. Used by tracker to detect stale signals on D3+."""
    try:
        stock = {
            "ticker":   ticker,
            "market":   market,
            "currency": "CAD" if market == "TSX" else "USD",
            "sector":   ""
        }
        result = compute_signal(stock, 1, 1)
        if result is None:
            return {"error": f"Could not compute signal for {ticker}"}
        return {
            "ticker":    ticker,
            "market":    market,
            "cms":       result["cms"],
            "rsi":       result["rsi"],
            "adx":       result["adx"],
            "tm_score":  result["tm_score"],
            "pq_score":  result["pq_score"],
            "vc_score":  result["vc_score"],
            "adx_score": result["adx_score"],
            "price":     result["price"],
            "trend_on":  result["above_200"]   # FIX #2: now resolves correctly
        }
    except Exception as e:
        return {"error": str(e)}


# ── CANDLES ENDPOINT ──────────────────────────────────────────────────────────

@app.get("/candles/{ticker}")
def get_candles(ticker: str, market: str = "TSX", interval: str = "5m", session: str = "today"):
    """
    Fetch intraday candles for a ticker.
    session=today    → live candles from today's open (market hours only)
    session=previous → last 30 min of previous session (3:30–4:00 PM ET)
    Returns raw candles + pre-computed metrics for Claude to interpret.
    """
    try:
        yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker
        et        = pytz.timezone("America/New_York")
        now_et    = datetime.now(et)

        raw = yf.download(
            yf_ticker,
            period="2d",
            interval=interval,
            progress=False,
            auto_adjust=True
        )

        if raw.empty or len(raw) < 4:
            return {"error": f"No intraday data available for {ticker}"}

        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)

        if raw.index.tz is None:
            raw.index = raw.index.tz_localize("UTC").tz_convert(et)
        else:
            raw.index = raw.index.tz_convert(et)

        today_str = now_et.strftime("%Y-%m-%d")

        if session == "today":
            df = raw[raw.index.strftime("%Y-%m-%d") == today_str]
            df = df[df.index.hour >= 9]
        else:
            # Previous session: last 30 min (3:30–4:00 PM ET)
            all_dates  = sorted(set(raw.index.strftime("%Y-%m-%d")))
            prev_dates = [d for d in all_dates if d < today_str]
            if not prev_dates:
                prev_dates = [all_dates[0]]
            prev_date = prev_dates[-1]
            day_df    = raw[raw.index.strftime("%Y-%m-%d") == prev_date]
            df = day_df[(day_df.index.hour > 15) |
                        ((day_df.index.hour == 15) & (day_df.index.minute >= 30))]

        if df.empty or len(df) < 2:
            return {
                "error":   f"Insufficient candle data for {ticker} ({session} session)",
                "candles": [],
                "metrics": {}
            }

        close  = df["Close"].squeeze().astype(float)
        high   = df["High"].squeeze().astype(float)
        low    = df["Low"].squeeze().astype(float)
        volume = df["Volume"].squeeze().astype(float)
        open_  = df["Open"].squeeze().astype(float)

        # VWAP
        typical  = (high + low + close) / 3
        vwap     = float((typical * volume).cumsum().iloc[-1] / volume.cumsum().iloc[-1])

        first_close      = float(close.iloc[0])
        last_close       = float(close.iloc[-1])
        price_change_pct = round((last_close - first_close) / first_close * 100, 2)

        mid             = max(1, len(volume) // 2)
        vol_first_half  = float(volume.iloc[:mid].mean())
        vol_second_half = float(volume.iloc[mid:].mean())
        vol_trend = "increasing" if vol_second_half > vol_first_half * 1.1 else \
                    "decreasing" if vol_second_half < vol_first_half * 0.9 else "steady"

        green_candles = int(((close - open_) > 0).sum())
        red_candles   = int(((close - open_) < 0).sum())
        green_vol     = float(volume[close > open_].sum())
        red_vol       = float(volume[close < open_].sum())
        total_vol     = float(volume.sum())
        buy_vol_pct   = round(green_vol / total_vol * 100, 1) if total_vol > 0 else 50.0

        session_high   = float(high.max())
        session_low    = float(low.min())
        rng            = session_high - session_low
        close_strength = round((last_close - session_low) / rng * 100, 1) if rng > 0 else 50.0

        if len(high) >= 4:
            recent_highs = list(high.iloc[-4:])
            recent_lows  = list(low.iloc[-4:])
            hh = all(recent_highs[i] > recent_highs[i-1] for i in range(1, len(recent_highs)))
            ll = all(recent_lows[i]  < recent_lows[i-1]  for i in range(1, len(recent_lows)))
            hl = all(recent_lows[i]  > recent_lows[i-1]  for i in range(1, len(recent_lows)))
        else:
            hh = ll = hl = False

        above_vwap = last_close > vwap

        ims_score = 0.0
        if price_change_pct > 0:     ims_score += 0.30
        if vol_trend == "increasing": ims_score += 0.25
        if close_strength >= 60:      ims_score += 0.25
        if above_vwap:                ims_score += 0.10
        if hh or hl:                  ims_score += 0.10
        ims_score = round(ims_score, 2)

        if price_change_pct > 0.3 and green_candles > red_candles and buy_vol_pct >= 55:
            trend = "TRENDING_UP"
        elif price_change_pct < -0.3 and red_candles > green_candles and buy_vol_pct < 45:
            trend = "TRENDING_DOWN"
        else:
            trend = "SIDEWAYS"

        candles = []
        for ts, row in df.iterrows():
            candles.append({
                "time":   ts.strftime("%H:%M"),
                "open":   round(float(row["Open"]), 2),
                "high":   round(float(row["High"]), 2),
                "low":    round(float(row["Low"]), 2),
                "close":  round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
                "green":  float(row["Close"]) >= float(row["Open"])
            })

        return {
            "ticker":   ticker,
            "market":   market,
            "interval": interval,
            "session":  session,
            "candles":  candles,
            "metrics": {
                "vwap":             round(vwap, 2),
                "price_change_pct": price_change_pct,
                "vol_trend":        vol_trend,
                "green_candles":    green_candles,
                "red_candles":      red_candles,
                "buy_vol_pct":      buy_vol_pct,
                "close_strength":   close_strength,
                "above_vwap":       above_vwap,
                "session_high":     round(session_high, 2),
                "session_low":      round(session_low, 2),
                "higher_highs":     hh,
                "higher_lows":      hl,
                "lower_lows":       ll,
                "trend":            trend,
                "ims_score":        ims_score,
                "candle_count":     len(candles)
            }
        }

    except Exception as e:
        print(f"CANDLES ERROR {ticker}: {e}")
        return {"error": str(e)}


@app.get("/scan")
def scan_all():
    results = sequential_scan(FULL_UNIVERSE)
    return {
        "signals":       results,
        "scanned_at":    datetime.now().isoformat(),
        "total":         len(results),
        "buy_signals":   sum(1 for r in results if r["entry_signal"]),
        "universe_size": len(FULL_UNIVERSE)
    }

@app.get("/scan/tsx")
def scan_tsx():
    results = sequential_scan(TSX_UNIVERSE)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/scan/us")
def scan_us():
    results = sequential_scan(US_UNIVERSE)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/scan/sector/{sector_name}")
def scan_sector(sector_name: str):
    universe = [s for s in FULL_UNIVERSE if s["sector"].lower() == sector_name.lower()]
    if not universe:
        return {"error": f"No stocks found for sector: {sector_name}"}
    results = sequential_scan(universe)
    return {"signals": results, "sector": sector_name, "scanned_at": datetime.now().isoformat()}

@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    for stock in FULL_UNIVERSE:
        if stock["ticker"] == ticker.upper():
            result = compute_signal(stock, 1, 1)
            return result if result else {"error": "Insufficient data"}
    return {"error": "Ticker not in universe"}

@app.get("/debug/{ticker}")
def debug_ticker(ticker: str, market: str = "NYSE"):
    try:
        yf_ticker    = f"{ticker}.TO" if market == "TSX" else ticker
        df           = download_single(yf_ticker)
        in_universe  = any(s["ticker"] == ticker.upper() for s in FULL_UNIVERSE)
        return {
            "ticker":            ticker,
            "yf_ticker":         yf_ticker,
            "in_universe":       in_universe,
            "rows_downloaded":   len(df),
            "passes_data_check": len(df) >= 200,
            "columns":           df.columns.tolist() if not df.empty else [],
            "last_close":        round(float(df["Close"].iloc[-1]), 2) if len(df) > 0 else None,
            "last_date":         str(df.index[-1]) if len(df) > 0 else None
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

@app.get("/track/{ticker}/{signal_date}")
def track_signal(ticker: str, signal_date: str, market: str = "TSX"):
    try:
        yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker
        print(f"TRACK REQUEST: {ticker} market={market} yf_ticker={yf_ticker} date={signal_date}")

        signal_dt = pd.to_datetime(signal_date)

        # Bounded date fetch — prevents back-fill bug where all 15 rows get same date.
        # 25 calendar days covers 15 trading days including weekends + holidays.
        start_str = signal_dt.strftime("%Y-%m-%d")
        end_dt    = signal_dt + pd.Timedelta(days=25)
        end_str   = end_dt.strftime("%Y-%m-%d")

        df = yf.download(
            yf_ticker,
            start=start_str,
            end=end_str,
            interval="1d",
            progress=False,
            auto_adjust=True,
            group_by="ticker"
        )

        if df is None or df.empty:
            return {"error": f"No data returned for {ticker}"}

        if isinstance(df.columns, pd.MultiIndex):
            level_0 = [str(v) for v in df.columns.get_level_values(0)]
            level_1 = [str(v) for v in df.columns.get_level_values(1)]
            if "Close" in level_0:
                df.columns = df.columns.droplevel(1)
            elif "Close" in level_1:
                df.columns = df.columns.droplevel(0)
            else:
                df.columns = [str(c[0]) for c in df.columns]

        df.columns = [str(c) for c in df.columns]
        if "Close" not in df.columns:
            return {"error": f"No Close column for {ticker}"}

        df = df[~df.index.duplicated(keep="last")]
        df = df.dropna(subset=["Close", "High", "Low"])
        df.index = pd.to_datetime(df.index).tz_localize(None)

        df_after = df[df.index >= signal_dt].head(15)

        if df_after.empty:
            return {"error": "No data after signal date"}

        days = []
        for i, (date, row) in enumerate(df_after.iterrows()):
            d1_close = round(float(row["Close"]), 2)
            days.append({
                "day":    i + 1,
                "date":   date.strftime("%Y-%m-%d"),
                "open":   round(float(row["Open"]), 2),
                "close":  d1_close,
                "high":   round(float(row["High"]), 2),
                "low":    round(float(row["Low"]), 2),
                "midday": round((float(row["High"]) + float(row["Low"])) / 2, 2),
            })

        first_close = days[0]["close"] if days else "N/A"
        print(f"TRACK {ticker}: {len(days)} days from {signal_date}, D1 close=${first_close}")
        return {"ticker": ticker, "signal_date": signal_date, "days": days}

    except Exception as e:
        print(f"Track error {ticker}: {e}")
        return {"error": str(e)}


# ── NEWS SYNTHESIS PROXY ──────────────────────────────────────────────────────

class SynthesizeRequest(BaseModel):
    ticker:      str
    price:       float
    currency:    str
    signal_type: str
    headlines:   list

@app.post("/synthesize")
async def synthesize_news(req: SynthesizeRequest):
    try:
        headline_text = ""
        if req.headlines:
            lines = []
            for i, h in enumerate(req.headlines, 1):
                lines.append(f"{i}. [{h.get('time','')} {h.get('source','')}] {h.get('headline','')}")
            headline_text = "\n".join(lines)
        else:
            headline_text = "No news headlines found in the last 24 hours."

        prompt = f"""You are a professional equity trading analyst. Assess whether overnight news supports or undermines a momentum buy signal.

Stock: {req.ticker}
Currency: {req.currency}
Current Price: {req.price}
Signal Type: {req.signal_type}

Overnight news headlines (last 24 hours):
{headline_text}

Respond in this exact JSON format with no markdown:
{{
  "verdict": "PROCEED" or "CAUTION" or "AVOID" or "NEUTRAL",
  "brief": "2-3 sentence synthesis. What happened overnight, how it affects this trade, and what to watch at market open. Be specific and actionable.",
  "key_risk": "One sentence on the main risk to the trade today, or null if none."
}}

Rules:
- PROCEED = news is supportive or neutral, signal intact
- CAUTION = mixed signals, wait for open confirmation
- AVOID = negative news materially changes risk/reward today
- NEUTRAL = no relevant news, assess on technicals alone
- Keep the brief under 60 words, direct and actionable"""

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return {"verdict": "NEUTRAL", "brief": "News synthesis unavailable — ANTHROPIC_API_KEY not set on server.", "key_risk": None}

        client  = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        text  = message.content[0].text
        import json, re
        clean  = re.sub(r"```json|```", "", text).strip()
        result = json.loads(clean)
        return result

    except Exception as e:
        print(f"Synthesis error for {req.ticker}: {e}")
        return {"verdict": "NEUTRAL", "brief": "Unable to synthesize news at this time.", "key_risk": None}


# ── HEALTH ────────────────────────────────────────────────────────────────────
# FIX #1: Single authoritative /health endpoint (duplicate stub removed)

@app.get("/health")
def health():
    return {
        "status":         "ok",
        "time":           datetime.now().isoformat(),
        "tsx_universe":   len(TSX_UNIVERSE),
        "us_universe":    len(US_UNIVERSE),
        "total_universe": len(FULL_UNIVERSE)
    }
