import math
import yfinance as yf
from datetime import datetime
from scipy.stats import norm
from scipy.optimize import brentq


# ── Black-Scholes ─────────────────────────────────────────
def black_scholes(S, K, T, r, sigma, option_type='call'):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return round(price, 4)


# ── Fetch Data ────────────────────────────────────────────
ticker = yf.Ticker("JPM")
S      = ticker.fast_info['last_price']

# Nearest expiry (topmost / first in list)
expiry = ticker.options[0]
T      = (datetime.strptime(expiry, "%Y-%m-%d") - datetime.today()).days / 365

# ── Pull Strike = 310 ─────────────────────────────────────
calls = ticker.option_chain(expiry).calls
row   = calls[calls['strike'] == 310].iloc[0]

K         = row['strike']
sigma     = row['impliedVolatility']
bid       = row['bid']
ask       = row['ask']
mid_price = round((bid + ask) / 2, 4)
r         = 0.045

# ── BS Price ──────────────────────────────────────────────
bs_price  = black_scholes(S, K, T, r, sigma)
diff      = round(bs_price - mid_price, 4)
diff_pct  = round((diff / mid_price) * 100, 2)

# ── True IV back-solved from mid ──────────────────────────
true_iv = brentq(lambda sig: black_scholes(S, K, T, r, sig) - mid_price, 0.001, 10)

# ── Output ────────────────────────────────────────────────
print(f"Expiry        : {expiry}")
print(f"Stock (S)     : ${S}")
print(f"Strike (K)    : ${K}")
print(f"T (years)     : {round(T, 4)}")
print(f"yf IV         : {round(sigma, 4)}")
print(f"True IV (mid) : {round(true_iv, 4)}")
print(f"Bid/Ask       : ${bid} / ${ask}  →  Mid: ${mid_price}")
print(f"BS Price      : ${bs_price}")
print(f"Diff          : ${diff} ({diff_pct}%)")

if abs(diff_pct) < 5:
    print("✅ Model close to market")
elif diff_pct > 0:
    print("📈 BS OVERPRICES vs market")
else:
    print("📉 BS UNDERPRICES vs market")