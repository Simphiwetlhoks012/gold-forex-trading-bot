# Gold & Forex Trading Bot

A phone-friendly Streamlit app prototype for Gold and Forex.

Features:
- XAUUSD proxy (GC=F), EUR/USD, GBP/USD, USD/JPY
- Live-ish market data refresh
- Price chart
- SMA20, SMA50, RSI
- BUY/SELL/HOLD signals
- Virtual R10,000 paper trading
- Backtesting
- Trade history
- Risk setting

Run:
pip install -r requirements.txt
streamlit run app.py

This version does NOT place real orders. A broker/API connection must be added separately after paper testing.
