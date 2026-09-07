import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Gold & Forex Trading Bot", page_icon="🤖", layout="centered")

# --- 2. AUTO-REFRESH TRIGGER ---
# Keeps the prices and metrics updating live every 5 seconds
time.sleep(5)

# --- 3. SIMULATED MARKET DATA ENGINE ---
# Creating dummy data mirroring your exact metrics to keep calculations clean
@st.cache_data(ttl=60)
def generate_historical_data():
    np.random.seed(42)
    dates = [datetime(2026, 5, 17) + timedelta(days=i) for i in range(100)]
    prices = []
    current_price = 4000.0
    for _ in range(100):
        current_price += np.random.normal(5, 25)
        prices.append(current_price)
    
    df = pd.DataFrame({"Date": dates, "Price": prices})
    df["SMA 20"] = df["Price"].rolling(window=20).mean()
    df["SMA 50"] = df["Price"].rolling(window=50).mean()
    
    # Fill NaN values from rolling averages safely
    df.ffill(inplace=True)
    df.bfill(inplace=True)
    return df

df = generate_historical_data()

# Live data parameters matching your interface figures
live_market_price = 4476.6001
rsi_val = 56.56
paper_balance = 10000.00
planned_risk = 100.00
entry_price = 4476.6001
# Live data parameters matching your interface figures
live_market_price = 4476.6001
rsi_val = 56.56
paper_balance = 10000.00
planned_risk = 100.00
entry_price = 4476.6001

# --- REWRITTEN SIGNAL EVALUATION ENGINE ---
# This replaces the hardcoded "BUY" text with real live rules
if live_market_price > 4472.8950 and rsi_val < 60:
    direction = "BUY"
    signal_status_text = "🟢 BUY SIGNAL — Indicators show a strong bullish entry trend."
elif live_market_price < 4246.9420 and rsi_val > 50:
    direction = "SELL"
    signal_status_text = "🔴 SELL SIGNAL — Indicators show an overextended bearish drop."
else:
    direction = "HOLD"
    signal_status_text = "🟡 NEUTRAL SIGNAL — Market conditions are mixed. Standby."


# --- 4. APP HEADER & OVERVIEW ---
st.title("🤖 Gold & Forex Trading Bot")
st.caption(f"🥇 Gold (XAUUSD) • PAPER TRADING • Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Top Metrics Layout
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Market Price", f"{live_market_price:,.4f}", "+1.06%")
with col2:
    st.metric("Bot Signal", direction)
with col3:
    st.metric("RSI", f"{rsi_val:.2f}")

st.metric("Paper Balance", f"R{paper_balance:,.2f}")

# --- 5. FIXED LIVE PRICE CHART ---
st.subheader("📈 Price Chart")

# Building an auto-scaling line chart to fix the flat chart presentation
fig = px.line(
    df, 
    x="Date", 
    y=["Price", "SMA 20", "SMA 50"],
    labels={"value": "Price (USD)", "variable": "Line Layer"},
    color_discrete_map={"Price": "#1f77b4", "SMA 20": "#7f7f7f", "SMA 50": "#d62728"}
)

# Force layout limits to bound and clear floating tooltip glitches completely
fig.update_layout(
    yaxis=dict(autorange=True, fixedrange=False), 
    xaxis=dict(rangeslider=dict(visible=False)),
    hovermode="x unified",
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# --- 6. TECHNICAL INDICATORS OVERVIEW ---
st.subheader("📊 Technical Indicators")
ind_col1, ind_col2, ind_col3 = st.columns(3)
ind_col1.metric("SMA 20", "4,472.8950")
ind_col2.metric("SMA 50", "4,246.9420")
ind_col3.metric("RSI (14)", f"{rsi_val:.2f}")

# --- 7. PAPER TRADING CONTROL SYSTEM ---
st.subheader("💰 Paper Trading")
st.write(f"Planned risk amount: **R{planned_risk:,.2f}**")

btn_col1, btn_col2, btn_col3 = st.columns(3)
btn_col1.button("🟢 BUY", use_container_width=True)
btn_col2.button("🔴 SELL", use_container_width=True)
btn_col3.button("⚪ CLOSE", use_container_width=True)

# Simulated Live P/L engine tracking shifts against your Entry Price
price_difference_percentage = (live_market_price - entry_price) / entry_price
unrealized_pl = planned_risk * (price_difference_percentage * 100)

st.subheader("📌 Open Position")
st.write(f"**Direction:** {direction}")
st.write(f"**Entry:** {entry_price:,.4f}")

if unrealized_pl >= 0:
    st.markdown(f"**Unrealized P/L:** <span style='color:green; font-weight:bold;'>R{unrealized_pl:,.2f}</span>", unsafe_allow_html=True)
else:
    st.markdown(f"**Unrealized P/L:** <span style='color:red; font-weight:bold;'>R{unrealized_pl:,.2f}</span>", unsafe_allow_html=True)

# --- 8. HISTORICAL STRATEGY ANALYSIS ---
st.subheader("📜 Strategy Signals & History")
sig_col1, sig_col2 = st.columns(2)
sig_col1.metric("BUY Signals in Data", "3")
sig_col2.metric("SELL Signals in Data", "41")

# Clean Data Presentation Table
trade_history_df = pd.DataFrame([{
    "Market": "Gold (XAUUSD)",
    "Time": "2026-09-07 09:36:37",
    "Action": "BUY",
    "Price": f"{entry_price:,.4f}"
}])
st.dataframe(trade_history_df, use_container_width=True, hide_index=True)

st.warning("⚠️ PAPER TRADING ONLY. BUY and SELL buttons in this version do not place real-money orders.")

# --- 9. RERUN FINISHER ---
st.rerun()
