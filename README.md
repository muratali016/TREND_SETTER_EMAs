# MAIN 5/9/20 EMA + VWAP + CFO Dashboard — TradingView Pine Script (v5)

A comprehensive intraday research and paper-trading tool built using **Pine Script v5**, combining EMA trend structure, VWAP behavior, volatility bands, relative volume, angle-based momentum detection, and a CFO-style dashboard for real-time market context.

This script was developed as part of my **Data Analytics Programming** final project, where it helped analyze time-of-day volatility patterns and algorithmic signal behavior.  
**Paper-trading accuracy:** 85.7% (educational use only — *not financial advice*).

---

## 🔧 Features

### 📌 Trend & Momentum Engine
- **EMA-5 / EMA-9 crossover system**  
- **EMA-20 trend baseline**  
- Automatic detection of:  
  - Bullish trend start (5 > 9 > 20)  
  - Bearish trend start (5 < 9 < 20)  
  - Angle-based momentum confirmation  
  - Optional over-extension detection  

### 📌 VWAP-Based Market Structure
- VWAP with **dynamic standard deviation bands**  
- Z-score distance from VWAP  
- Strong VWAP trend detection (5 > 9 > VWAP > 20)

### 📌 Relative Volume (RVOL)
- High-volume confirmations  
- Multi-bar pattern checks  
- RVOL display on dashboard

### 📌 CFO Dashboard
Displays the most important intraday quantitative metrics:
- VIX  
- ADR (10-day average daily range)  
- Expected Move (% via VIX/16)  
- ADX (trend strength)  
- RVOL  
- VWAP deviation (σ)  

### 📌 Alerts
Includes 10+ TradingView alert conditions:
- EMA cross signals  
- Trend alignment  
- Strong VWAP alignment  
- High-volatility confirmations  

### 📌 Visual Enhancements
- Trend-colored candles  
- Buy/Sell labels  
- VWAP band fills  
- Dashboard (bottom-right)

---

## 📊 Example Use Cases
- Intraday volatility analysis  
- Studying algorithmic momentum & trend behavior  
- Understanding VWAP deviation cycles  
- Paper trading strategy development  
- Educational market microstructure research  

---

## 🧩 File Structure

