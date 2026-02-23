from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── UNIVERSE ──────────────────────────────────────────────────────────────────

TSX_UNIVERSE = [
    # Financials (15)
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
    {"ticker":"FSZ",  "market":"TSX","currency":"CAD","sector":"Financials"},
    # Energy (15)
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
    # Materials (15)
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
    {"ticker":"SSL",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"NGT",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"EDV",  "market":"TSX","currency":"CAD","sector":"Materials"},
    {"ticker":"DPM",  "market":"TSX","currency":"CAD","sector":"Materials"},
    # Technology (15)
    {"ticker":"SHOP", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"CSU",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"ENGH", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"KXS",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"DCBO", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"LSPD", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"NVEI", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"CDAY", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"TOI",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"DSGX", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"BBTV", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"SSNC", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"GIB",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"MDA",  "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"QTRH", "market":"TSX","currency":"CAD","sector":"Technology"},
    # Industrials (15)
    {"ticker":"CP",   "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"CN",   "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"CAE",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TRI",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"WSP",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"STN",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TFI",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"BYD",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"SNC",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"NFI",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"RUS",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"GFL",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"WCN",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"ABT",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TFII", "market":"TSX","currency":"CAD","sector":"Industrials"},
    # Consumer (15)
    {"ticker":"MRU",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"L",    "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"DOL",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"ATD",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"QSR",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"EMP",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"PZA",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"MTY",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"GIL",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"RCH",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"CTC",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"ACB",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"JWEL", "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"SCI",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"BPF",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    # Utilities (15)
    {"ticker":"FTS",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"AQN",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"H",    "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"NPI",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"BEP",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"CPX",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"EMA",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"INE",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"ALA",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"CU",   "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"FOR",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"BLX",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"PPL",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"KEY",  "market":"TSX","currency":"CAD","sector":"Utilities"},
    {"ticker":"TA",   "market":"TSX","currency":"CAD","sector":"Utilities"},
    # Healthcare (15)
    {"ticker":"NVO",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"CLS",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"WELL", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"GUD",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"DND",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"HLS",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"CATO", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"PBH",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"CURA", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"TRIL", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"PRYM", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"BUZZ", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"VHI",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"DNLI", "market":"TSX","currency":"CAD","sector":"Healthcare"},
    {"ticker":"ADW",  "market":"TSX","currency":"CAD","sector":"Healthcare"},
]

US_UNIVERSE = [
    # Technology (15)
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
    # Financials (15)
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
    # Healthcare (15)
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
    # Energy (15)
    {"ticker":"XOM",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"CVX",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"COP",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"EOG",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"SLB",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"MPC",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"PSX",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"VLO",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"PXD",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"HAL",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"DVN",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"FANG", "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"OXY",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"HES",  "market":"NYSE","currency":"USD","sector":"Energy"},
    {"ticker":"BKR",  "market":"NYSE","currency":"USD","sector":"Energy"},
    # Consumer (15)
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
    {"ticker":"EL",   "market":"NYSE","currency":"USD","sector":"Consumer"},
    # Industrials (15)
    {"ticker":"CAT",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"DE",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"HON",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"UPS",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"RTX",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"LMT",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"GE",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"MMM",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"BA",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"FDX",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"EMR",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"ETN",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"PH",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"GD",   "market":"NYSE","currency":"USD","sector":"Industrials"},
    {"ticker":"NOC",  "market":"NYSE","currency":"USD","sector":"Industrials"},
    # Materials (15)
    {"ticker":"LIN",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"APD",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"SHW",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"ECL",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"NEM",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"FCX",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"NUE",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"VMC",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"MLM",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"DOW",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"DD",   "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"ALB",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"CF",   "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"MOS",  "market":"NYSE","currency":"USD","sector":"Materials"},
    {"ticker":"AA",   "market":"NYSE","currency":"USD","sector":"Materials"},
    # Utilities (15)
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
    {"ticker":"AES",  "market":"NYSE","currency":"USD","sector":"Utilities"},
    # ETFs
    {"ticker":"SPY",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"QQQ",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLF",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLE",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"GLD",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLV",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLI",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLB",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLU",  "market":"NYSE","currency":"USD","sector":"ETF"},
    {"ticker":"XLK",  "market":"NYSE","currency":"USD","sector":"ETF"},
]

# ── DEDUPLICATE ───────────────────────────────────────────────────────────────
# First deduplicate US universe on its own
seen = set()
_deduped = []
for s in US_UNIVERSE:
    if s["ticker"] not in seen:
        seen.add(s["ticker"])
        _deduped.append(s)
US_UNIVERSE = _deduped

# Then deduplicate the full combined universe
seen2 = set()
_final = []
for s in TSX_UNIVERSE + US_UNIVERSE:
    if s["ticker"] not in seen2:
        seen2.add(s["ticker"])
        _final.append(s)
FULL_UNIVERSE = _final


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

def safe_download(yf_ticker: str, retries: int = 3) -> pd.DataFrame:
    """
    Downloads with retry logic to handle yfinance rate limiting.
    Parallel threads often trigger rate limits causing empty returns.
    """
    import time
    for attempt in range(retries):
        try:
            df = yf.download(
                yf_ticker,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True
            )
            if len(df) >= 50:
                return df
            wait = (attempt + 1) * 2
            print(f"RETRY {yf_ticker} attempt {attempt+1}: only {len(df)} rows, waiting {wait}s")
            time.sleep(wait)
        except Exception as e:
            wait = (attempt + 1) * 2
            print(f"RETRY {yf_ticker} attempt {attempt+1} error: {e}, waiting {wait}s")
            time.sleep(wait)
    print(f"FAILED {yf_ticker}: all {retries} attempts exhausted")
    return pd.DataFrame()


def compute_signal(stock: dict) -> dict:
    ticker   = stock["ticker"]
    market   = stock["market"]
    currency = stock["currency"]
    sector   = stock.get("sector", "")

    yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker

    try:
        df = safe_download(yf_ticker)

        if len(df) < 200:
            print(f"SKIP {ticker}: only {len(df)} rows")
            return None

        # Bulletproof MultiIndex fix
        # yfinance can return (field, ticker) or (ticker, field) — handle both
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
            print(f"SKIP {ticker}: no Close column. Got: {df.columns.tolist()}")
            return None

        close  = df["Close"].squeeze()
        volume = df["Volume"].squeeze()
        high   = df["High"].squeeze()
        low    = df["Low"].squeeze()

        mask   = close.notna() & volume.notna() & high.notna() & low.notna()
        close  = close[mask]
        volume = volume[mask]
        high   = high[mask]
        low    = low[mask]

        if len(close) < 200:
            print(f"SKIP {ticker}: only {len(close)} clean rows after NaN drop")
            return None

        # Signal 1: MACD Momentum
        macd_ind = ta.trend.MACD(close, window_slow=21, window_fast=9, window_sign=9)
        hist     = macd_ind.macd_diff()
        tm_score = 1 if (hist.iloc[-1] > 0 and hist.iloc[-1] > hist.iloc[-2]) else 0

        # Signal 2: RSI + SMA Pullback Quality
        rsi_series    = ta.momentum.RSIIndicator(close, window=14).rsi()
        rsi_val       = float(rsi_series.iloc[-1])
        sma50         = close.rolling(50).mean()
        sma200        = close.rolling(200).mean()
        current_price = float(close.iloc[-1])
        pq_score = 1 if (40 <= rsi_val <= 60 and current_price > float(sma50.iloc[-1])) else 0

        # Signal 3: Volume + OBV
        vol_sma   = volume.rolling(20).mean()
        vol_ratio = float(volume.iloc[-1] / vol_sma.iloc[-1])
        obv       = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
        obv_slope = float(obv.iloc[-1] - obv.iloc[-6])
        vc_score  = 1 if (vol_ratio < 0.8 and obv_slope > 0) else 0

        # ATR for stop calculation
        atr = float(ta.volatility.AverageTrueRange(
            high, low, close, window=14).average_true_range().iloc[-1])

        # CMS Score
        cms       = round((tm_score * 0.45) + (pq_score * 0.35) + (vc_score * 0.20), 3)
        above_200 = current_price > float(sma200.iloc[-1])
        confirm   = current_price > float(close.iloc[-2])

        # Only check earnings for stocks with a meaningful CMS score
        earnings_info = {"near_earnings": False, "earnings_date": None}
        if cms >= 0.60:
            earnings_info = is_near_earnings(ticker, market)

        # Entry signal — blocked if near earnings
        entry_signal = (
            cms >= 0.80
            and above_200
            and confirm
            and rsi_val < 70
            and not earnings_info["near_earnings"]
        )

        stop = round(max(current_price - 2.0 * atr, current_price * 0.93), 2)

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
            "entry_signal":     entry_signal,
            "earnings_blocked": earnings_info["near_earnings"],
            "earnings_date":    earnings_info.get("earnings_date"),
            "days_to_earnings": earnings_info.get("days_to_earnings"),
            "stop":             stop,
            "target_1":         round(current_price * 1.08, 2),
            "target_2":         round(current_price * 1.15, 2),
            "signal_strength":  "STRONG" if cms >= 0.80 else "MODERATE" if cms >= 0.60 else "WEAK",
            "timestamp":        datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error computing {ticker}: {e}")
        return None


# ── PARALLEL SCAN ENGINE ──────────────────────────────────────────────────────

def parallel_scan(universe: list, max_workers: int = 6) -> list:
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(compute_signal, stock): stock for stock in universe}
        for future in as_completed(futures):
            try:
                result = future.result(timeout=30)
                if result:
                    results.append(result)
            except Exception as e:
                stock = futures[future]
                print(f"Parallel error {stock['ticker']}: {e}")
    return sorted(results, key=lambda x: x["cms"], reverse=True)


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/scan")
def scan_all():
    results = parallel_scan(FULL_UNIVERSE)
    return {
        "signals":       results,
        "scanned_at":    datetime.now().isoformat(),
        "total":         len(results),
        "buy_signals":   sum(1 for r in results if r["entry_signal"]),
        "universe_size": len(FULL_UNIVERSE)
    }

@app.get("/scan/tsx")
def scan_tsx():
    results = parallel_scan(TSX_UNIVERSE)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/scan/us")
def scan_us():
    results = parallel_scan(US_UNIVERSE)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/scan/sector/{sector_name}")
def scan_sector(sector_name: str):
    universe = [s for s in FULL_UNIVERSE if s["sector"].lower() == sector_name.lower()]
    if not universe:
        return {"error": f"No stocks found for sector: {sector_name}"}
    results = parallel_scan(universe)
    return {"signals": results, "sector": sector_name, "scanned_at": datetime.now().isoformat()}

@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    for stock in FULL_UNIVERSE:
        if stock["ticker"] == ticker.upper():
            result = compute_signal(stock)
            return result if result else {"error": "Insufficient data"}
    return {"error": "Ticker not in universe"}

@app.get("/debug/{ticker}")
def debug_ticker(ticker: str, market: str = "NYSE"):
    """Check exactly why a stock might be missing from scan results"""
    try:
        yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker
        df = safe_download(yf_ticker)
        if isinstance(df.columns, pd.MultiIndex):
            level_0 = [str(v) for v in df.columns.get_level_values(0)]
            if "Close" in level_0:
                df.columns = df.columns.droplevel(1)
            else:
                df.columns = df.columns.droplevel(0)
        in_universe = any(s["ticker"] == ticker.upper() for s in FULL_UNIVERSE)
        return {
            "ticker":             ticker,
            "yf_ticker":          yf_ticker,
            "in_universe":        in_universe,
            "rows_downloaded":    len(df),
            "passes_data_check":  len(df) >= 200,
            "last_close":         round(float(df["Close"].iloc[-1]), 2) if len(df) > 0 else None,
            "last_date":          str(df.index[-1]) if len(df) > 0 else None
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}

@app.get("/track/{ticker}/{signal_date}")
def track_signal(ticker: str, signal_date: str, market: str = "TSX"):
    try:
        yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker
        df = yf.download(yf_ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            level_0 = [str(v) for v in df.columns.get_level_values(0)]
            if "Close" in level_0:
                df.columns = df.columns.droplevel(1)
            else:
                df.columns = df.columns.droplevel(0)
        df.index = pd.to_datetime(df.index).tz_localize(None)
        signal_dt = pd.to_datetime(signal_date)
        df_after = df[df.index >= signal_dt].head(15)
        if df_after.empty:
            return {"error": "No data after signal date"}
        days = []
        for i, (date, row) in enumerate(df_after.iterrows()):
            days.append({
                "day":    i + 1,
                "date":   date.strftime("%Y-%m-%d"),
                "open":   round(float(row["Open"]), 2),
                "close":  round(float(row["Close"]), 2),
                "high":   round(float(row["High"]), 2),
                "low":    round(float(row["Low"]), 2),
                "midday": round((float(row["High"]) + float(row["Low"])) / 2, 2),
            })
        return {"ticker": ticker, "signal_date": signal_date, "days": days}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    return {
        "status":         "ok",
        "time":           datetime.now().isoformat(),
        "tsx_universe":   len(TSX_UNIVERSE),
        "us_universe":    len(US_UNIVERSE),
        "total_universe": len(FULL_UNIVERSE)
    }
