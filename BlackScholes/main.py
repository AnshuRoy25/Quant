import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Options Viewer", layout="wide")
st.title("Options Chain Viewer")

R = 0.045

STOCKS = {
    "Wells Fargo (WFC)"    : "WFC",
    "JPMorgan Chase (JPM)" : "JPM",
    "HSBC Holdings (HSBC)" : "HSBC",
    "Barclays (BCS)"       : "BCS",
    "Deutsche Bank (DB)"   : "DB",
}

def get_moneyness(S, K):
    pct = (S - K) / K * 100
    if pct > 2:    return "ITM"
    elif pct < -2: return "OTM"
    else:          return "ATM"

# ── Controls ──────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    name   = st.selectbox("Stock", list(STOCKS.keys()))
    symbol = STOCKS[name]

with col3:
    opt_type = st.radio("Option Type", ["Calls", "Puts"])

# ── Fetch stock info (no caching, avoids serialization issues) ────
try:
    ticker   = yf.Ticker(symbol)
    hist     = ticker.history(period="1d")
    S        = float(hist["Close"].iloc[-1]) if not hist.empty else None
    prev     = float(hist["Open"].iloc[-1])  if not hist.empty else None
    expiries = list(ticker.options)
except Exception as e:
    st.error(f"Failed to fetch {symbol}: {e}")
    st.stop()

if not S:
    st.error("Could not get stock price. Try another ticker.")
    st.stop()

with col2:
    expiry = st.selectbox("Expiry Date", expiries)

T = max((datetime.strptime(expiry, "%Y-%m-%d") - datetime.today()).days / 365, 1/365)

# ── Stock Snapshot ─────────────────────────────────────────
st.subheader(f"{symbol} — ${S:.2f}")
change = S - prev if prev else 0
c1, c2, c3, c4 = st.columns(4)
c1.metric("Last Price",    f"${S:.2f}")
c2.metric("Day Change",    f"${change:.2f}", f"{change/prev*100:.2f}%" if prev else "")
c3.metric("T (years)",     f"{T:.4f}")
c4.metric("Risk-free (r)", f"{R*100:.1f}%")

st.divider()

# ── Options Chain ──────────────────────────────────────────
st.subheader(f"{opt_type} Chain — {expiry}")

try:
    chain = ticker.option_chain(expiry)
    df    = chain.calls if opt_type == "Calls" else chain.puts
except Exception as e:
    st.error(f"Could not load chain: {e}")
    st.stop()

if df.empty:
    st.warning("No data for this expiry.")
    st.stop()

keep = ['strike', 'bid', 'ask', 'lastPrice', 'impliedVolatility', 'volume', 'openInterest']
df   = df[[c for c in keep if c in df.columns]].copy()
df['mid']       = ((df['bid'] + df['ask']) / 2).round(4)
df['moneyness'] = df['strike'].apply(lambda k: get_moneyness(S, k))
df['IV %']      = (df['impliedVolatility'] * 100).round(2).astype(str) + "%"

df = df.rename(columns={
    'strike'           : 'Strike (K)',
    'bid'              : 'Bid',
    'ask'              : 'Ask',
    'lastPrice'        : 'Last Price',
    'impliedVolatility': 'IV_raw',
    'volume'           : 'Volume',
    'openInterest'     : 'Open Interest',
    'mid'              : 'Mid',
    'moneyness'        : 'Moneyness',
})

display_cols = ['Strike (K)', 'Moneyness', 'Bid', 'Ask', 'Mid', 'Last Price', 'IV %', 'Volume', 'Open Interest']
st.dataframe(df[[c for c in display_cols if c in df.columns]], use_container_width=True, hide_index=True)

st.divider()

# ── BS Inputs ──────────────────────────────────────────────
st.subheader("Black-Scholes Inputs")
st.caption("Pick a strike to see the 5 inputs ready for the BS formula")

strikes = sorted(df['Strike (K)'].tolist())
default = min(strikes, key=lambda k: abs(k - S))
K_sel   = st.select_slider("Strike Price", options=strikes, value=default)

row    = df[df['Strike (K)'] == K_sel].iloc[0]
iv_sel = float(row['IV_raw']) if 'IV_raw' in df.columns else None
mid_s  = round((float(row['Bid']) + float(row['Ask'])) / 2, 4)

b1, b2, b3, b4, b5 = st.columns(5)
b1.metric("S — Stock Price",  f"${S:.2f}")
b2.metric("K — Strike",       f"${K_sel}")
b3.metric("T — Time (years)", f"{T:.4f}")
b4.metric("r — Risk-free",    f"{R*100:.2f}%")
b5.metric("σ — Implied Vol",  f"{iv_sel*100:.2f}%" if iv_sel else "N/A")

st.info(f"Mid Price (market): **${mid_s}** — this is what we'll compare our BS price against in Phase 2")