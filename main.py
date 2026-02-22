from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime

app = FastAPI()

app.add_middleware(from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# TSX stocks use .TO suffix, US stocks use no suffix
TSX_UNIVERSE = [
    {"ticker": "RY",   "market": "TSX", "currency": "CAD"},
    {"ticker": "TD",   "market": "TSX", "currency": "CAD"},
    {"ticker": "BNS",  "market": "TSX", "currency": "CAD"},
    {"ticker": "BMO",  "market": "TSX", "currency": "CAD"},
    {"ticker": "CM",   "market": "TSX", "currency": "CAD"},
    {"ticker": "CNQ",  "market": "TSX", "currency": "CAD"},
    {"ticker": "SU",   "market": "TSX", "currency": "CAD"},
    {"ticker": "CVE",  "market": "TSX", "currency": "CAD"},
    {"ticker": "TOU",  "market": "TSX", "currency": "CAD"},
    {"ticker": "ABX",  "market": "TSX", "currency": "CAD"},
    {"ticker": "WPM",  "market": "TSX", "currency": "CAD"},
    {"ticker": "FM",   "market": "TSX", "currency": "CAD"},
    {"ticker": "SHOP", "market": "TSX", "currency": "CAD"},
    {"ticker": "CSU",  "market": "TSX", "currency": "CAD"},
    {"ticker": "CP",   "market": "TSX", "currency": "CAD"},
    {"ticker": "CN",   "market": "TSX", "currency": "CAD"},
    {"ticker": "MRU",  "market": "TSX", "currency": "CAD"},
    {"ticker": "L",    "market": "TSX", "currency": "CAD"},
]

US_UNIVERSE = [
    {"ticker": "AAPL",  "market": "NYSE", "currency": "USD"},
    {"ticker": "MSFT",  "market": "NYSE", "currency": "USD"},
    {"ticker": "NVDA",  "market": "NYSE", "currency": "USD"},
    {"ticker": "AMZN",  "market": "NYSE", "currency": "USD"},
    {"ticker": "GOOGL", "market": "NYSE", "currency": "USD"},
    {"ticker": "META",  "market": "NYSE", "currency": "USD"},
    {"ticker": "TSLA",  "market": "NYSE", "currency": "USD"},
    {"ticker": "JPM",   "market": "NYSE", "currency": "USD"},
    {"ticker": "V",     "market": "NYSE", "currency": "USD"},
    {"ticker": "SPY",   "market": "NYSE", "currency": "USD"},
    {"ticker": "QQQ",   "market": "NYSE", "currency": "USD"},
    {"ticker": "XLF",   "market": "NYSE", "currency": "USD"},
    {"ticker": "XLE",   "market": "NYSE", "currency": "USD"},
    {"ticker": "GLD",   "market": "NYSE", "currency": "USD"},
]

FULL_UNIVERSE = TSX_UNIVERSE + US_UNIVERSE

def compute_signal(stock: dict) -> dict:
    ticker   = stock["ticker"]
    market   = stock["market"]
    currency = stock["currency"]

    # TSX needs .TO suffix for yfinance
    yf_ticker = f"{ticker}.TO" if market == "TSX" else ticker

    df = yf.download(yf_ticker, period="1y", interval="1d", progress=False)
    if len(df) < 210:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    close  = df['Close']
    volume = df['Volume']
    high   = df['High']
    low    = df['Low']

    # MACD
    macd_ind = ta.trend.MACD(close, window_slow=21, window_fast=9, window_sign=9)
    hist     = macd_ind.macd_diff()
    tm_score = 1 if (hist.iloc[-1] > 0 and hist.iloc[-1] > hist.iloc[-2]) else 0

    # RSI + SMAs
    rsi_series   = ta.momentum.RSIIndicator(close, window=14).rsi()
    rsi_val      = float(rsi_series.iloc[-1])
    sma50        = close.rolling(50).mean()
    sma200       = close.rolling(200).mean()
    current_price = float(close.iloc[-1])

    pq_score = 1 if (40 <= rsi_val <= 60 and current_price > float(sma50.iloc[-1])) else 0

    # Volume + OBV
    vol_sma   = volume.rolling(20).mean()
    vol_ratio = float(volume.iloc[-1] / vol_sma.iloc[-1])
    obv       = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
    obv_slope = float(obv.iloc[-1] - obv.iloc[-6])
    vc_score  = 1 if (vol_ratio < 0.8 and obv_slope > 0) else 0

    # ATR
    atr = float(ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range().iloc[-1])

    cms        = round((tm_score * 0.45) + (pq_score * 0.35) + (vc_score * 0.20), 3)
    above_200  = current_price > float(sma200.iloc[-1])
    confirm    = current_price > float(close.iloc[-2])
    entry_signal = cms >= 0.80 and above_200 and confirm and rsi_val < 70

    stop = round(max(current_price - 2.0 * atr, current_price * 0.93), 2)

    return {
        "ticker":          ticker,
        "market":          market,
        "currency":        currency,
        "price":           round(current_price, 2),
        "cms":             cms,
        "rsi":             round(rsi_val, 2),
        "tm_score":        tm_score,
        "pq_score":        pq_score,
        "vc_score":        vc_score,
        "entry_signal":    entry_signal,
        "stop":            stop,
        "target_1":        round(current_price * 1.08, 2),
        "target_2":        round(current_price * 1.15, 2),
        "signal_strength": "STRONG" if cms >= 0.80 else "MODERATE" if cms >= 0.60 else "WEAK",
        "timestamp":       datetime.now().isoformat()
    }

@app.get("/scan")
def scan_all():
    results = []
    for stock in FULL_UNIVERSE:
        try:
            signal = compute_signal(stock)
            if signal:
                results.append(signal)
        except Exception as e:
            print(f"Error {stock['ticker']}: {e}")
    results.sort(key=lambda x: x["cms"], reverse=True)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/scan/tsx")
def scan_tsx():
    results = []
    for stock in TSX_UNIVERSE:
        try:
            signal = compute_signal(stock)
            if signal:
                results.append(signal)
        except Exception as e:
            print(f"Error {stock['ticker']}: {e}")
    results.sort(key=lambda x: x["cms"], reverse=True)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/scan/us")
def scan_us():
    results = []
    for stock in US_UNIVERSE:
        try:
            signal = compute_signal(stock)
            if signal:
                results.append(signal)
        except Exception as e:
            print(f"Error {stock['ticker']}: {e}")
    results.sort(key=lambda x: x["cms"], reverse=True)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    for stock in FULL_UNIVERSE:
        if stock["ticker"] == ticker.upper():
            result = compute_signal(stock)
            return result if result else {"error": "Insufficient data"}
    return {"error": "Ticker not in universe"}

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TSX_UNIVERSE = [
    "RY", "TD", "BNS", "BMO", "CM",
    "CNQ", "SU", "CVE", "TOU",
    "ABX", "WPM", "FM",
    "SHOP", "CSU", "CP", "CN", "MRU", "L"
]

def compute_signal(ticker: str) -> dict:
    df = yf.download(f"{ticker}.TO", period="1y", interval="1d", progress=False)
    if len(df) < 210:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    close = df['Close']
    volume = df['Volume']
    high = df['High']
    low = df['Low']

    # MACD
    macd = ta.trend.MACD(close, window_slow=21, window_fast=9, window_sign=9)
    hist = macd.macd_diff()
    tm_score = 1 if (hist.iloc[-1] > 0 and hist.iloc[-1] > hist.iloc[-2]) else 0

    # RSI
    rsi_series = ta.momentum.RSIIndicator(close, window=14).rsi()
    rsi_val = float(rsi_series.iloc[-1])

    # SMAs
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    current_price = float(close.iloc[-1])

    pq_score = 1 if (40 <= rsi_val <= 60 and current_price > float(sma50.iloc[-1])) else 0

    # Volume + OBV
    vol_sma = volume.rolling(20).mean()
    vol_ratio = float(volume.iloc[-1] / vol_sma.iloc[-1])
    obv = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
    obv_slope = float(obv.iloc[-1] - obv.iloc[-6])
    vc_score = 1 if (vol_ratio < 0.8 and obv_slope > 0) else 0

    # ATR
    atr = float(ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range().iloc[-1])

    cms = round((tm_score * 0.45) + (pq_score * 0.35) + (vc_score * 0.20), 3)
    above_200 = current_price > float(sma200.iloc[-1])
    confirmation = current_price > float(close.iloc[-2])
    entry_signal = cms >= 0.80 and above_200 and confirmation and rsi_val < 70

    stop = round(max(current_price - 2.0 * atr, current_price * 0.93), 2)

    return {
        "ticker": ticker,
        "price": round(current_price, 2),
        "cms": cms,
        "rsi": round(rsi_val, 2),
        "tm_score": tm_score,
        "pq_score": pq_score,
        "vc_score": vc_score,
        "entry_signal": entry_signal,
        "stop": stop,
        "target_1": round(current_price * 1.08, 2),
        "target_2": round(current_price * 1.15, 2),
        "signal_strength": "STRONG" if cms >= 0.80 else "MODERATE" if cms >= 0.60 else "WEAK",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/scan")
def scan_all():
    results = []
    for ticker in TSX_UNIVERSE:
        try:
            signal = compute_signal(ticker)
            if signal:
                results.append(signal)
        except Exception as e:
            print(f"Error {ticker}: {e}")
    results.sort(key=lambda x: x["cms"], reverse=True)
    return {"signals": results, "scanned_at": datetime.now().isoformat()}

@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    result = compute_signal(ticker.upper())
    if not result:
        return {"error": "Insufficient data"}
    return result

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}
