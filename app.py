import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Gold & Forex Bot", page_icon="🤖", layout="wide")

MARKETS = {
    "🥇 Gold (XAUUSD)": "GC=F",
    "💵 EUR/USD": "EURUSD=X",
    "🇬🇧 GBP/USD": "GBPUSD=X",
    "🇯🇵 USD/JPY": "JPY=X",
}

@st.cache_data(ttl=60)
def load_data(symbol, period="6mo"):
    df = yf.download(symbol, period=period, interval="1d",
                     auto_adjust=False, progress=False)
    if df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.dropna().copy()

    close = pd.to_numeric(df["Close"], errors="coerce")
    df["SMA20"] = close.rolling(20).mean()
    df["SMA50"] = close.rolling(50).mean()

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df.dropna()

def signal_for(df):
    if df.empty:
        return "WAIT", "No market data"
    r = df.iloc[-1]
    p, s20, s50, rsi = map(float, [r["Close"], r["SMA20"], r["SMA50"], r["RSI"]])
    if p > s20 > s50 and 30 < rsi < 70:
        return "BUY", "Uptrend + RSI confirmation"
    if p < s20 < s50 and 30 < rsi < 70:
        return "SELL", "Downtrend + RSI confirmation"
    return "HOLD", "Conditions not aligned"

def backtest(df, risk_pct):
    balance = 10000.0
    position = 0.0
    entry = 0.0
    curve, closed = [], []

    for _, row in df.iterrows():
        price = float(row["Close"])
        s20, s50, rsi = row["SMA20"], row["SMA50"], row["RSI"]
        if pd.isna(s20) or pd.isna(s50) or pd.isna(rsi):
            curve.append(balance)
            continue

        buy = price > s20 > s50 and 30 < rsi < 70
        sell = price < s20 < s50 and 30 < rsi < 70

        if position == 0 and buy:
            risk_cash = balance * risk_pct / 100
            position = risk_cash / max(price, 1e-9)
            entry = price
        elif position > 0 and sell:
            pnl = (price - entry) * position
            balance += pnl
            closed.append(pnl)
            position = 0.0
            entry = 0.0

        curve.append(balance + (position * price if position else 0))

    if position:
        final_price = float(df["Close"].iloc[-1])
        balance += (final_price - entry) * position
        closed.append((final_price - entry) * position)

    trades = len(closed)
    wins = sum(x > 0 for x in closed)
    return {
        "final": balance,
        "pnl": balance - 10000,
        "return_pct": (balance / 10000 - 1) * 100,
        "trades": trades,
        "win_rate": wins / trades * 100 if trades else 0,
        "curve": curve,
    }

if "cash" not in st.session_state:
    st.session_state.cash = 10000.0
if "position" not in st.session_state:
    st.session_state.position = 0.0
if "entry_price" not in st.session_state:
    st.session_state.entry_price = 0.0
if "trades" not in st.session_state:
    st.session_state.trades = []

st.sidebar.title("🤖 Gold & Forex Bot")
market_name = st.sidebar.selectbox("Market", list(MARKETS.keys()))
symbol = MARKETS[market_name]
period = st.sidebar.selectbox("History", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
st.sidebar.button("🔄 Refresh market data")
risk = st.sidebar.slider("Risk per trade (%)", 0.25, 5.0, 1.0, 0.25)

st.sidebar.divider()
st.sidebar.success("🟢 Market data: ON")
st.sidebar.warning("🟡 Broker: NOT CONNECTED")
st.sidebar.caption("This version cannot place real orders.")

df = load_data(symbol, period)
if df.empty:
    st.error("Market data could not be loaded. Try again or choose another market.")
    st.stop()

price = float(df["Close"].iloc[-1])
previous = float(df["Close"].iloc[-2])
change_pct = (price / previous - 1) * 100
sig, reason = signal_for(df)
portfolio = st.session_state.cash + st.session_state.position * price

st.title("🤖 Gold & Forex Trading Bot")
st.caption(f"{market_name} • {symbol} • Updated {datetime.now().strftime('%H:%M:%S')}")

a, b, c, d = st.columns(4)
a.metric("Market price", f"{price:,.4f}", f"{change_pct:+.2f}%")
b.metric("Signal", sig)
c.metric("Paper balance", f"R{st.session_state.cash:,.2f}")
d.metric("Paper equity", f"R{portfolio:,.2f}")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 Bot", "🧪 Backtest", "📜 History"])

with tab1:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Price chart")
        st.line_chart(df[["Close", "SMA20", "SMA50"]])
    with right:
        st.subheader("Analysis")
        st.metric("SMA 20", f"{float(df['SMA20'].iloc[-1]):,.4f}")
        st.metric("SMA 50", f"{float(df['SMA50'].iloc[-1]):,.4f}")
        st.metric("RSI 14", f"{float(df['RSI'].iloc[-1]):,.1f}")
        if sig == "BUY":
            st.success(f"🟢 BUY\n\n{reason}")
        elif sig == "SELL":
            st.error(f"🔴 SELL\n\n{reason}")
        else:
            st.info(f"🟡 HOLD\n\n{reason}")

with tab2:
    st.subheader("Paper trading")
    st.info("Virtual money only. No broker order is sent.")
    x, y, z = st.columns(3)

    with x:
        if st.button("🟢 BUY", use_container_width=True):
            if st.session_state.position == 0:
                risk_cash = st.session_state.cash * risk / 100
                qty = risk_cash / max(price, 1e-9)
                st.session_state.position = qty
                st.session_state.entry_price = price
                st.session_state.trades.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "market": market_name, "action": "BUY",
                    "price": price, "pnl": 0.0
                })
                st.success(f"Paper BUY opened at {price:,.4f}")
            else:
                st.warning("A paper position is already open.")

    with y:
        if st.button("🔴 SELL", use_container_width=True):
            if st.session_state.position > 0:
                pnl = (price - st.session_state.entry_price) * st.session_state.position
                st.session_state.cash += st.session_state.position * price
                st.session_state.position = 0.0
                st.session_state.trades.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "market": market_name, "action": "SELL",
                    "price": price, "pnl": pnl
                })
                st.success(f"Paper SELL closed. P/L: R{pnl:,.2f}")
            else:
                st.warning("No paper position is open.")

    with z:
        if st.button("⏹ Close position", use_container_width=True):
            if st.session_state.position > 0:
                pnl = (price - st.session_state.entry_price) * st.session_state.position
                st.session_state.cash += st.session_state.position * price
                st.session_state.position = 0.0
                st.session_state.trades.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "market": market_name, "action": "CLOSE",
                    "price": price, "pnl": pnl
                })
                st.success(f"Position closed. P/L: R{pnl:,.2f}")
            else:
                st.info("No open position.")

    st.write(f"**Position:** {st.session_state.position:.8f}")
    if st.session_state.position:
        st.write(f"**Entry price:** {st.session_state.entry_price:,.4f}")

with tab3:
    st.subheader("Historical backtest")
    st.caption("A backtest is not a guarantee of future profit.")
    result = backtest(df, risk)
    a, b, c, d = st.columns(4)
    a.metric("Final balance", f"R{result['final']:,.2f}")
    b.metric("P/L", f"R{result['pnl']:,.2f}")
    c.metric("Return", f"{result['return_pct']:.2f}%")
    d.metric("Win rate", f"{result['win_rate']:.1f}%")
    st.line_chart(pd.DataFrame({"Equity": result["curve"]}))
    st.write(f"Completed trades: **{result['trades']}**")

with tab4:
    st.subheader("Trade history")
    if st.session_state.trades:
        st.dataframe(pd.DataFrame(st.session_state.trades), use_container_width=True)
    else:
        st.info("No paper trades yet.")

st.divider()
st.caption("⚠️ Prototype only. Market data may be delayed. Real trading requires a supported broker API, credentials and additional safeguards.")
