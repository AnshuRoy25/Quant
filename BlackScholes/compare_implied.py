import math
import pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
from datetime import datetime

# ── BS Formula ────────────────────────────────────────────
def black_scholes(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

# ── Back-solve IV from mid price ──────────────────────────
def calc_true_iv(S, K, T, r, mid_price):
    try:
        return round(brentq(
            lambda sig: black_scholes(S, K, T, r, sig) - mid_price,
            0.001, 50.0  # wide range for deep ITM
        ), 4)
    except:
        return None

# ── Inputs ────────────────────────────────────────────────
S = 311.02       # JPM stock price
r = 0.045
T = (datetime(2026, 4, 17) - datetime.today()).days / 365

# ── Data ──────────────────────────────────────────────────
data = [
    (165, 144.90, 147.25),
    (180, 130.15, 132.60),
    (185, 124.95, 126.90),
    (190, 119.95, 122.25),
    (195, 114.95, 117.05),
    (200, 109.95, 112.40),
    (205, 104.95, 107.05),
    (210,  99.95, 101.95),
    (215,  94.95,  97.10),
    (220,  90.00,  92.35),
    (225,  84.95,  87.10),
    (230,  80.00,  82.45),
    (235,  75.00,  77.30),
    (240,  70.00,  72.15),
    (245,  65.00,  67.20),
]

# ── Calculate & Print ─────────────────────────────────────
print(f"S = ${S},  T = {round(T,4)} years,  r = {r}")
print("=" * 45)
print(f"{'Strike':>8} {'Mid':>8} {'True IV':>10}")
print("-" * 45)

for K, bid, ask in data:
    mid = round((bid + ask) / 2, 4)
    iv  = calc_true_iv(S, K, T, r, mid)
    iv_str = f"{round(iv*100, 2)}%" if iv else "N/A"
    print(f"  K={K:>6}   Mid=${mid:>7}   IV={iv_str}")