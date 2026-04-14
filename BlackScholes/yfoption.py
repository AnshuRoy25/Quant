import yfinance as yf
from datetime import datetime

ticker = yf.Ticker("JPM")

# ── S: Current Stock Price ────────────────────────────────
S = ticker.fast_info['last_price']
print(f"S (Current Price): {S}")

# ── Expiry dates available ────────────────────────────────
expiries = ticker.options
print(f"\nAvailable Expiries: {expiries}")

# Pick the first expiry (e.g. nearest one)
expiry = expiries[0]

# ── T: Time to Expiry in Years ────────────────────────────
expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
today = datetime.today()
T = (expiry_date - today).days / 365
print(f"\nT (Time to Expiry in Years): {round(T, 4)}")

# ── Options Chain for that expiry ────────────────────────
chain = ticker.option_chain(expiry)
calls = chain.calls

print(f"\nCalls Chain Sample:\n{calls[['strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility', 'volume', 'openInterest']].head(10)}")

# ── K, sigma, LTP: Pick a specific strike ────────────────
# Let's pick the strike closest to current price (ATM)
calls['diff'] = abs(calls['strike'] - S)
atm_row = calls.loc[calls['diff'].idxmin()]

K     = atm_row['strike']
sigma = atm_row['impliedVolatility']
LTP   = atm_row['lastPrice']          # ← Option's Last Traded Price

print(f"\nK     (Strike, ATM):       {K}")
print(f"sigma (Implied Vol):       {round(sigma, 4)}")
print(f"LTP   (Option Last Price): {LTP}")

# ── r: Risk-free rate (manual — 10Y treasury approx) ─────
r = 0.045
print(f"r     (Risk-free rate):    {r}")

# ── Summary ───────────────────────────────────────────────
print("\n--- Black-Scholes Inputs ---")
print(f"S     = {S}")
print(f"K     = {K}")
print(f"T     = {round(T, 4)}")
print(f"r     = {r}")
print(f"sigma = {round(sigma, 4)}")
print(f"LTP   = {LTP}")