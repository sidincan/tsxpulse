from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import requests
import os

app = FastAPI()

# Allow your Lovable frontend to call this API
app.add_middleware(
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
    
    # Flatten multi-level columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    
    close = df['Close']
    volume = df['Volume']
    high = df['High']
    low = df['Low']

    # MACD
    macd_df = ta.macd(close, fast=9, slow=21, signal=9)
    hist_col = [c for c in macd_df.columns if 'MACDh' in c][0]
    hist = macd_df[hist_col]
    tm_score = 1 if (hist.iloc[-1] > 0 and hist.iloc[-1] > hist.iloc[-2]) else 0

    # RSI + SMAs
    rsi_series = ta.rsi(close, length=14)
    sma50 = ta.sma(close, length=50)
    sma200 = ta.sma(close, length=200)
    rsi_val = float(rsi_series.iloc[-1])
    current_price = float(close.iloc[-1])

    pq_score = 1 if (40 <= rsi_val <= 60 and current_price > float(sma50.iloc[-1])) else 0

    # Volume + OBV
    vol_sma = volume.rolling(20).mean()
    vol_ratio = float(volume.iloc[-1] / vol_sma.iloc[-1])
    obv = ta.obv(close, volume)
    obv_slope = float(obv.iloc[-1] - obv.iloc[-6])
    vc_score = 1 if (vol_ratio < 0.8 and obv_slope > 0) else 0

    cms = round((tm_score * 0.45) + (pq_score * 0.35) + (vc_score * 0.20), 3)

    above_200 = current_price > float(sma200.iloc[-1])
    confirmation = current_price > float(close.iloc[-2])
    entry_signal = cms >= 0.80 and above_200 and confirmation and rsi_val < 70

    atr = float(ta.atr(high, low, close, length=14).iloc[-1])
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