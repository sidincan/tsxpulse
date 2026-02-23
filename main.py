from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import time

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
    {"ticker":"NGT",  "market":"TSX","currency":"CAD","sector":"Materials"},
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
    {"ticker":"BBTV", "market":"TSX","currency":"CAD","sector":"Technology"},
    {"ticker":"GIB",  "market":"TSX","currency":"CAD","sector":"Technology"},
    # Industrials
    {"ticker":"CP",   "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"CN",   "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"CAE",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TRI",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"WSP",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"STN",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TFI",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"BYD",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"GFL",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"WCN",  "market":"TSX","currency":"CAD","sector":"Industrials"},
    {"ticker":"TFII", "market":"TSX","currency":"CAD","sector":"Industrials"},
    # Consumer
    {"ticker":"MRU",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"L",    "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"DOL",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"ATD",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"QSR",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"MTY",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"GIL",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"CTC",  "market":"TSX","currency":"CAD","sector":"Consumer"},
    {"ticker":"ATD",  "market":"TSX","currency":"CAD","sector":"Consumer"},
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

TSX_UNIVERSE = dedup(TSX_UNIVERSE)
US_UNIVERSE  = dedup(US_UNIVERSE)
FULL_UNIVERSE = dedup(TSX_UNIVERSE + US_UNIVERSE)


# ── DATA DOWNLOAD — SEQUENTIAL, ONE STOCK AT A TIME ──────────────────────────

def download_single(yf_ticker: str) -> pd.DataFrame:
    """
    Downloads one stock sequentially. No parallel calls to yfinance.
    This is the only reliable way to get clean 1D data per stock.
    """
    try:
        df = yf.download(
            yf_ticker,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
            group_by="ticker"   # forces clean single-stock format
        )
        if df is None or df.empty:
            return pd.DataFrame()

        # Flatten MultiIndex if present
        if isinstance(df.columns, pd.MultiIndex):
            # With group_by="ticker", format is (field, ticker) — drop ticker level
            level_0 = [str(v) for v in df.columns.get_level_values(0)]
            level_1 = [str(v) for v in df.columns.get_level_values(1)]
            if "Close" in level_0:
                df.columns = df.columns.droplevel(1)
            elif "Close" in level_1:
                df.columns = df.columns.droplevel(0)
            else:
                # last resort
                df.columns = [str(c[0]) for c in df.columns]

        df.columns = [str(c) for c in df.columns]

        if "Close" not in df.columns:
            return pd.DataFrame()

        # Remove duplicate index entries (cause "cannot reindex" errors)
        df = df[~df.index.duplicated(keep="last")]

        # Drop NaN rows
        df = df.dropna(subset=["Close", "High", "Low", "Volume"])

        return df

    except Exception as e:
        print(f"Download error {yf_ticker}: {e}")
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

        # Verify all are 1D Series
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
        pq_score = 1 if (40 <= rsi_val <= 60 and current_price > float(sma50.iloc[-1])) else 0

        # Signal 3: Volume + OBV
        vol_ratio = float(volume.iloc[-1] / volume.rolling(20).mean().iloc[-1])
        obv       = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
        obv_slope = float(obv.iloc[-1] - obv.iloc[-6])
        vc_score  = 1 if (vol_ratio < 0.8 and obv_slope > 0) else 0

        # ATR
        atr = float(ta.volatility.AverageTrueRange(
            high, low, close, window=14).average_true_range().iloc[-1])

        # ADX — measures trend strength (not direction)
        # ADX > 25 = strong directional trend, < 20 = choppy/sideways
        adx_val = float(ta.trend.ADXIndicator(high, low, close, window=14).adx().iloc[-1])
        adx_score = 1 if adx_val >= 25 else 0

        # CMS Score — ADX replaces volume as 4th signal, reweighted
        cms       = round((tm_score * 0.40) + (pq_score * 0.30) + (vc_score * 0.15) + (adx_score * 0.15), 3)
        above_200 = current_price > float(sma200.iloc[-1])
        confirm   = current_price > float(close.iloc[-2])

        earnings_info = {"near_earnings": False, "earnings_date": None}
        if cms >= 0.60:
            earnings_info = is_near_earnings(ticker, market)

        entry_signal = (
            cms >= 0.80
            and above_200
            and confirm
            and rsi_val < 70
            and adx_val >= 25          # trend must be strong, not choppy
            and not earnings_info["near_earnings"]
        )

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
        print(f"Error computing {ticker} ({idx}/{total}): {e}")
        return None


# ── SEQUENTIAL SCAN ───────────────────────────────────────────────────────────

def sequential_scan(universe: list) -> list:
    """
    Scans stocks one at a time. Eliminates all parallel data corruption.
    Small delay between requests to avoid rate limiting.
    """
    results = []
    total = len(universe)
    for idx, stock in enumerate(universe, 1):
        result = compute_signal(stock, idx, total)
        if result:
            results.append(result)
        time.sleep(0.3)   # 300ms between requests — prevents rate limiting
    print(f"Scan complete: {len(results)}/{total} stocks processed")
    return sorted(results, key=lambda x: x["cms"], reverse=True)


# ── ROUTES ────────────────────────────────────────────────────────────────────

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
        yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker
        df = download_single(yf_ticker)
        in_universe = any(s["ticker"] == ticker.upper() for s in FULL_UNIVERSE)
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
        df = yf.download(yf_ticker, period="3mo", interval="1d",
                         progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            level_0 = [str(v) for v in df.columns.get_level_values(0)]
            df.columns = df.columns.droplevel(1) if "Close" in level_0 else df.columns.droplevel(0)
        df.columns = [str(c) for c in df.columns]
        df = df[~df.index.duplicated(keep="last")]
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
