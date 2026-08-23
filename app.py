import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# =========================================================
# GOLD & FOREX TRADING BOT
# PAPER TRADING VERSION
# =========================================================

st.set_page_config(
    page_title="Gold & Forex Trading Bot",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

if "balance" not in st.session_state:
    st.session_state.balance = 10000.00

if "position" not in st.session_state:
    st.session_state.position = None

if "entry_price" not in st.session_state:
    st.session_state.entry_price = 0.0

if "quantity" not in st.session_state:
    st.session_state.quantity = 0.0

if "history" not in st.session_state:
    st.session_state.history = []

# =========================================================
# MARKETS
# =========================================================

MARKETS = {
    "🥇 Gold (XAUUSD)": "GC=F",
    "💵 EUR/USD": "EURUSD=X",
    "🇬🇧 GBP/USD": "GBPUSD=X",
    "🇯🇵 USD/JPY": "JPY=X"
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Bot Settings")

asset = st.sidebar.selectbox(
    "Select market",
    list(MARKETS.keys())
)

symbol = MARKETS[asset]

risk_percent = st.sidebar.slider(
    "Risk per trade (%)",
    0.5,
    5.0,
    1.0,
    0.5
)

period = st.sidebar.selectbox(
    "Historical data",
    ["1mo", "3mo", "6mo", "1y", "2y"],
    index=2
)

interval = st.sidebar.selectbox(
    "Candle interval",
    ["1d", "1h"],
    index=0
)

# =========================================================
# DATA
# =========================================================

@st.cache_data(ttl=60)
def get_market_data(symbol, period, interval):

    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        required = ["Open", "High", "Low", "Close"]

        for column in required:
            if column not in df.columns:
                return pd.DataFrame()

        return df.dropna().copy()

    except Exception:
        return pd.DataFrame()


data = get_market_data(symbol, period, interval)

# =========================================================
# HEADER
# =========================================================

st.title("🤖 Gold & Forex Trading Bot")

st.caption(
    f"{asset} • PAPER TRADING • "
    f"Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

if data.empty:
    st.error(
        "Unable to retrieve market data right now. "
        "Try refreshing the app."
    )
    st.stop()

# =========================================================
# INDICATORS
# =========================================================

data["SMA20"] = data["Close"].rolling(20).mean()
data["SMA50"] = data["Close"].rolling(50).mean()

delta = data["Close"].diff()

gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss.replace(0, np.nan)

data["RSI"] = 100 - (100 / (1 + rs))

data = data.dropna().copy()

if len(data) < 2:
    st.error("Not enough market data.")
    st.stop()

current_price = float(data["Close"].iloc[-1])
previous_price = float(data["Close"].iloc[-2])

sma20 = float(data["SMA20"].iloc[-1])
sma50 = float(data["SMA50"].iloc[-1])
rsi = float(data["RSI"].iloc[-1])

change_percent = (
    (current_price - previous_price)
    / previous_price
) * 100

# =========================================================
# SIGNAL ENGINE
# =========================================================

if (
    current_price > sma20
    and sma20 > sma50
    and rsi < 70
):
    signal = "BUY"

elif (
    current_price < sma20
    and sma20 < sma50
    and rsi > 30
):
    signal = "SELL"

else:
    signal = "HOLD"

# =========================================================
# DASHBOARD
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Market Price",
        f"{current_price:,.4f}",
        f"{change_percent:+.2f}%"
    )

with c2:
    st.metric(
        "Bot Signal",
        signal
    )

with c3:
    st.metric(
        "RSI",
        f"{rsi:.2f}"
    )

with c4:
    st.metric(
        "Paper Balance",
        f"R{st.session_state.balance:,.2f}"
    )

# =========================================================
# SIGNAL STATUS
# =========================================================

if signal == "BUY":

    st.success(
        "🟢 BUY SIGNAL — strategy conditions are bullish."
    )

elif signal == "SELL":

    st.error(
        "🔴 SELL SIGNAL — strategy conditions are bearish."
    )

else:

    st.warning(
        "🟡 HOLD — no strong setup detected."
    )

# =========================================================
# CHART
# =========================================================

st.subheader("📈 Price Chart")

chart = data[
    ["Close", "SMA20", "SMA50"]
].rename(
    columns={
        "Close": "Price",
        "SMA20": "SMA 20",
        "SMA50": "SMA 50"
    }
)

st.line_chart(chart)

# =========================================================
# INDICATORS
# =========================================================

st.subheader("📊 Technical Indicators")

i1, i2, i3 = st.columns(3)

with i1:
    st.metric(
        "SMA 20",
        f"{sma20:,.4f}"
    )

with i2:
    st.metric(
        "SMA 50",
        f"{sma50:,.4f}"
    )

with i3:
    st.metric(
        "RSI",
        f"{rsi:.2f}"
    )

# =========================================================
# PAPER TRADING
# =========================================================

st.subheader("💰 Paper Trading")

risk_amount = (
    st.session_state.balance
    * risk_percent
    / 100
)

st.write(
    f"Planned risk amount: **R{risk_amount:,.2f}**"
)

b1, b2, b3 = st.columns(3)

# =========================================================
# BUY BUTTON
# =========================================================

with b1:

    if st.button(
        "🟢 BUY",
        use_container_width=True
    ):

        if st.session_state.position is None:

            st.session_state.position = "BUY"
            st.session_state.entry_price = current_price
            st.session_state.quantity = (
                risk_amount / current_price
            )

            st.session_state.history.append({
                "Time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "Market": asset,
                "Action": "BUY",
                "Price": current_price,
                "Quantity": st.session_state.quantity,
                "P/L": 0.0
            })

            st.success(
                f"Paper BUY opened at "
                f"{current_price:,.4f}"
            )

        else:

            st.warning(
                "You already have an open position."
            )

# =========================================================
# SELL BUTTON
# =========================================================

with b2:

    if st.button(
        "🔴 SELL",
        use_container_width=True
    ):

        if st.session_state.position is None:

            st.session_state.position = "SELL"
            st.session_state.entry_price = current_price
            st.session_state.quantity = (
                risk_amount / current_price
            )

            st.session_state.history.append({
                "Time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "Market": asset,
                "Action": "SELL",
                "Price": current_price,
                "Quantity": st.session_state.quantity,
                "P/L": 0.0
            })

            st.success(
                f"Paper SELL opened at "
                f"{current_price:,.4f}"
            )

        else:

            st.warning(
                "You already have an open position."
            )

# =========================================================
# CLOSE BUTTON
# =========================================================

with b3:

    if st.button(
        "⚪ CLOSE",
        use_container_width=True
    ):

        if st.session_state.position is None:

            st.info("There is no open position.")

        else:

            entry = st.session_state.entry_price
            quantity = st.session_state.quantity

            if st.session_state.position == "BUY":

                profit = (
                    current_price - entry
                ) * quantity

            else:

                profit = (
                    entry - current_price
                ) * quantity

            st.session_state.balance += profit

            st.session_state.history.append({
                "Time": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "Market": asset,
                "Action": "CLOSE",
                "Price": current_price,
                "Quantity": quantity,
                "P/L": profit
            })

            st.session_state.position = None
            st.session_state.entry_price = 0.0
            st.session_state.quantity = 0.0

            if profit >= 0:

                st.success(
                    f"Position closed. "
                    f"Profit: R{profit:,.2f}"
                )

            else:

                st.error(
                    f"Position closed. "
                    f"Loss: R{profit:,.2f}"
                )

# =========================================================
# CURRENT POSITION
# =========================================================

st.subheader("📌 Open Position")

if st.session_state.position is None:

    st.info("No open paper position.")

else:

    entry = st.session_state.entry_price
    quantity = st.session_state.quantity

    if st.session_state.position == "BUY":

        unrealized = (
            current_price - entry
        ) * quantity

    else:

        unrealized = (
            entry - current_price
        ) * quantity

    p1, p2, p3 = st.columns(3)

    with p1:
        st.write(
            f"**Direction:** "
            f"{st.session_state.position}"
        )

    with p2:
        st.write(
            f"**Entry:** "
            f"{entry:,.4f}"
        )

    with p3:
        st.write(
            f"**Unrealized P/L:** "
            f"R{unrealized:,.2f}"
        )

# =========================================================
# TRADE HISTORY
# =========================================================

st.subheader("📜 Trade History")

if st.session_state.history:

    history = pd.DataFrame(
        st.session_state.history
    )

    st.dataframe(
        history,
        use_container_width=True
    )

else:

    st.info(
        "No trades yet. "
        "Use BUY or SELL to create a paper trade."
    )

# =========================================================
# STRATEGY TEST
# =========================================================

st.subheader("🧪 Strategy Signals")

buy_condition = (
    (data["Close"] > data["SMA20"])
    & (data["SMA20"] > data["SMA50"])
    & (data["RSI"] < 70)
)

sell_condition = (
    (data["Close"] < data["SMA20"])
    & (data["SMA20"] < data["SMA50"])
    & (data["RSI"] > 30)
)

data["Signal"] = "HOLD"

data.loc[
    buy_condition,
    "Signal"
] = "BUY"

data.loc[
    sell_condition,
    "Signal"
] = "SELL"

s1, s2 = st.columns(2)

with s1:
    st.metric(
        "BUY signals in data",
        int((data["Signal"] == "BUY").sum())
    )

with s2:
    st.metric(
        "SELL signals in data",
        int((data["Signal"] == "SELL").sum())
    )

# =========================================================
# DISCLAIMER
# =========================================================

st.divider()

st.warning(
    "⚠️ PAPER TRADING ONLY. "
    "BUY and SELL buttons in this version do NOT place "
    "real-money orders. Market data may be delayed and "
    "may differ from a broker's executable price."
)
