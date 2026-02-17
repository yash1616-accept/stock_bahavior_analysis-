"""
===============================================================================
FLASK BACKEND API
Connects React UI to Python analysis pipeline
Run with: python app.py
API runs at: http://localhost:5000
===============================================================================
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import yfinance as yf
import os
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)  # Allow React (port 5173) to call this API

# ============================================================================
# HELPER: Feature Engineering
# ============================================================================
def engineer_features(df):
    df = df.copy()
    df["Price_Change_Pct"] = df["Close"].pct_change() * 100
    df["Volume_MA20"]  = df["Volume"].rolling(window=20, min_periods=1).mean()
    df["Volume_Mean"]  = df["Volume"].rolling(window=20, min_periods=1).mean()
    df["Volume_Std"]   = df["Volume"].rolling(window=20, min_periods=1).std()
    df["Volume_Zscore"]= (df["Volume"] - df["Volume_Mean"]) / df["Volume_Std"]
    df["Volume_Zscore"].fillna(0, inplace=True)
    df["Volatility"]   = df["Price_Change_Pct"].rolling(window=7, min_periods=1).std()
    df["Momentum_5d"]  = df["Close"].pct_change(periods=5) * 100
    df["Daily_Range"]  = ((df["High"] - df["Low"]) / df["Low"]) * 100
    return df

# ============================================================================
# HELPER: Behavior Detection
# ============================================================================
def detect_behavior(df):
    df = df.copy()
    df["Behavior"]         = "Normal"
    df["Confidence_Score"] = 0.0

    panic = (df["Price_Change_Pct"] < -2.5) & (df["Volume_Zscore"] > 1.5) & (df["Volatility"] > 2.0)
    fomo  = (df["Price_Change_Pct"] >  2.5) & (df["Volume_Zscore"] > 1.5) & (df["Volatility"] > 1.5)
    over  = (df["Price_Change_Pct"].abs() < 1.0) & (df["Volume_Zscore"] > 2.0) & (df["Volatility"] > 1.8)

    df.loc[panic, "Behavior"] = "Panic Selling"
    df.loc[fomo,  "Behavior"] = "FOMO Buying"
    df.loc[over,  "Behavior"] = "Overconfidence"

    df.loc[panic, "Confidence_Score"] = (
        df.loc[panic, "Price_Change_Pct"].abs() / 10 +
        df.loc[panic, "Volume_Zscore"] / 5 +
        df.loc[panic, "Volatility"] / 10
    ).clip(0, 1) * 100

    df.loc[fomo, "Confidence_Score"] = (
        df.loc[fomo, "Price_Change_Pct"] / 10 +
        df.loc[fomo, "Volume_Zscore"] / 5 +
        df.loc[fomo, "Volatility"] / 10
    ).clip(0, 1) * 100

    df.loc[over, "Confidence_Score"] = (
        df.loc[over, "Volume_Zscore"] / 5 +
        df.loc[over, "Volatility"] / 10
    ).clip(0, 1) * 100

    return df

# ============================================================================
# HELPER: Convert DataFrame to JSON-safe list
# ============================================================================
def df_to_records(df):
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                record[col] = None
            elif isinstance(val, (np.integer,)):
                record[col] = int(val)
            elif isinstance(val, (np.floating,)):
                record[col] = round(float(val), 4)
            else:
                record[col] = str(val)
        records.append(record)
    return records

# ============================================================================
# ROUTE 1: Health Check
# ============================================================================
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Backend is running!"})

# ============================================================================
# ROUTE 2: Analyze Stock from Yahoo Finance
# ============================================================================
@app.route("/api/analyze", methods=["GET"])
def analyze():
    ticker = request.args.get("ticker", "AAPL").upper()
    period = request.args.get("period", "6mo")

    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        df    = stock.history(period=period)

        if df.empty:
            return jsonify({"error": f"No data found for ticker: {ticker}"}), 404

        df.reset_index(inplace=True)

        # Format date
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

        # Keep only required columns
        df = df[["Date","Open","High","Low","Close","Volume"]].copy()
        df.columns = ["Date","Open","High","Low","Close","Volume"]

        # Feature Engineering + Behavior Detection
        df = engineer_features(df)
        df = detect_behavior(df)

        # Build summary stats
        behaviors    = df["Behavior"].value_counts().to_dict()
        total        = len(df)
        total_return = round(((df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0]) * 100, 2)
        avg_vol      = round(float(df["Volatility"].mean()), 2)
        max_vol      = round(float(df["Volatility"].max()), 2)
        risk_pct     = round((df[df["Behavior"] != "Normal"].shape[0] / total) * 100, 1)
        max_price    = round(float(df["High"].max()), 2)
        min_price    = round(float(df["Low"].min()), 2)

        # Recent 5-day insights
        recent5 = df.tail(5)["Behavior"].value_counts().to_dict()

        insights = []
        if recent5.get("Panic Selling", 0) >= 2:
            insights.append({"type": "warning", "title": "Recent Panic Selling",
                             "text": "Possible contrarian buying opportunity — validate fundamentals first."})
        if recent5.get("FOMO Buying", 0) >= 2:
            insights.append({"type": "caution", "title": "Recent FOMO Buying",
                             "text": "Stock may be overbought. Consider waiting for a pullback."})
        if recent5.get("Overconfidence", 0) >= 2:
            insights.append({"type": "info", "title": "Overtrading Detected",
                             "text": "Market is indecisive. Await a clear directional signal."})
        if recent5.get("Normal", 0) >= 4:
            insights.append({"type": "success", "title": "Stable Conditions",
                             "text": "No emotional trading detected recently — good entry environment."})

        return jsonify({
            "ticker":   ticker,
            "period":   period,
            "data":     df_to_records(df),
            "summary": {
                "total":        total,
                "behaviors":    behaviors,
                "total_return": total_return,
                "avg_volatility": avg_vol,
                "max_volatility": max_vol,
                "risk_pct":     risk_pct,
                "max_price":    max_price,
                "min_price":    min_price,
                "start_price":  round(float(df["Open"].iloc[0]), 2),
                "end_price":    round(float(df["Close"].iloc[-1]), 2),
            },
            "insights": insights
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ROUTE 3: Analyze Uploaded CSV/Excel File
# ============================================================================
@app.route("/api/analyze-file", methods=["POST"])
def analyze_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file   = request.files["file"]
    ticker = request.form.get("ticker", "UPLOADED").upper()

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Read file
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file)
        else:
            return jsonify({"error": "Unsupported file format. Use CSV or Excel."}), 400

        # Standardize column names
        col_map = {
            "date":"Date","datetime":"Date","timestamp":"Date",
            "open":"Open","o":"Open",
            "high":"High","h":"High",
            "low":"Low","l":"Low",
            "close":"Close","c":"Close","adj close":"Close",
            "volume":"Volume","vol":"Volume","v":"Volume"
        }
        df.columns = [col_map.get(c.lower().strip(), c.capitalize()) for c in df.columns]

        required = ["Date","Open","High","Low","Close","Volume"]
        missing  = [c for c in required if c not in df.columns]
        if missing:
            return jsonify({"error": f"Missing columns: {missing}"}), 400

        df = df[required].copy()

        # Clean
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
        for col in ["Open","High","Low","Close","Volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df.dropna(inplace=True)
        df.drop_duplicates(subset=["Date"], keep="first", inplace=True)
        df.sort_values("Date", inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Feature Engineering + Behavior Detection
        df = engineer_features(df)
        df = detect_behavior(df)

        behaviors    = df["Behavior"].value_counts().to_dict()
        total        = len(df)
        total_return = round(((df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0]) * 100, 2)
        avg_vol      = round(float(df["Volatility"].mean()), 2)
        max_vol      = round(float(df["Volatility"].max()), 2)
        risk_pct     = round((df[df["Behavior"] != "Normal"].shape[0] / total) * 100, 1)

        return jsonify({
            "ticker":  ticker,
            "period":  f"{total} days",
            "data":    df_to_records(df),
            "summary": {
                "total":          total,
                "behaviors":      behaviors,
                "total_return":   total_return,
                "avg_volatility": avg_vol,
                "max_volatility": max_vol,
                "risk_pct":       risk_pct,
                "max_price":      round(float(df["High"].max()), 2),
                "min_price":      round(float(df["Low"].min()), 2),
                "start_price":    round(float(df["Open"].iloc[0]), 2),
                "end_price":      round(float(df["Close"].iloc[-1]), 2),
            },
            "insights": []
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ROUTE 4: List available tickers info
# ============================================================================
@app.route("/api/tickers", methods=["GET"])
def tickers():
    return jsonify([
        {"label": "Apple (AAPL)",              "value": "AAPL"},
        {"label": "Tesla (TSLA)",              "value": "TSLA"},
        {"label": "Microsoft (MSFT)",          "value": "MSFT"},
        {"label": "Google (GOOGL)",            "value": "GOOGL"},
        {"label": "NVIDIA (NVDA)",             "value": "NVDA"},
        {"label": "Reliance (RELIANCE.NS)",    "value": "RELIANCE.NS"},
        {"label": "TCS (TCS.NS)",              "value": "TCS.NS"},
        {"label": "AB Capital (ABCAPITAL.NS)", "value": "ABCAPITAL.NS"},
    ])

# ============================================================================
# RUN
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 Stock Behaviour Analysis API")
    print("  Running at: http://localhost:5000")
    print("  Endpoints:")
    print("    GET  /api/health")
    print("    GET  /api/analyze?ticker=AAPL&period=6mo")
    print("    POST /api/analyze-file  (multipart/form-data)")
    print("    GET  /api/tickers")
    print("=" * 60)
    app.run(debug=True, port=5000)