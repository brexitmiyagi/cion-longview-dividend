# From the third quarter to a run-rate quarter without Longview.
# Everything here is my estimate. The day counts come from the dates in the 10-Q
# and 8-Ks; the yields are the company's own (10.58% on income-producing debt at
# cost) or the SLFP loan list. Change the assumptions and rerun.
import re
from common import inputs, rows, incentive_fee

I = inputs()
sofr = I['sofr_3m_2026_09_30']
sh = I['shares_outstanding_2026_09_30'] / 1000
YIELD_DEBT = 0.1058          # company: yield on debt and other income producing investments at cost, Q3
SLFP_PREF_RATE = 0.10        # my assumption, the 10-Q does not give the preferred return
SLFP_EXPENSES = 0.005        # my assumption, of loans per year

# SLFP loan yield from the 10-Q list (spread plus SOFR, floors respected; Prime loans at SOFR+3.0 as a rough proxy)
loans = rows('slfp_loans_2026_09_30.csv')
num = den = 0
for r in loans:
    fv = float(r['fair_value_k'])
    s = float(re.search(r'\+(\d+)', r['rate']).group(1)) / 10000
    base = sofr + 0.03 if r['rate'].startswith('Prime') else max(sofr, float(r['sofr_floor_pct'] or 0) / 100)
    num += fv * (base + s); den += fv
slfp_yield = num / den
print(f"SLFP loans: {len(loans)} loans, {den:,.0f}k at fair value, weighted all-in yield about {slfp_yield:.2%}")

import io, os, runpy, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    LD = runpy.run_path(os.path.join(HERE, 'longview_dividend.py'))
start = LD['adj_m']   # Q3 pre-incentive NII without Longview, one-offs added back on management's count (longview_dividend.py)
print(f"start: Q3 without Longview, management's one-offs added back {start:,.0f}k (my narrower count: {LD['adj']:,.0f}k)")
d = lambda days: days / 365
steps = [
    ('JPM facility gone (paid 86 days in Q3)', 200000 * (sofr + 0.0255 + 0.002) * d(86)),
    ('Series A notes gone (paid 62 days in Q3)', 114844 * (sofr + 0.0382) * d(62)),
    ('new 2029/2031 notes for a full quarter (about 31 more days)', -37000 * 0.0797 * d(31)),
    ('SLFP loans sold 17 Sep (held 78 days in Q3)', -180000 * slfp_yield * d(78)),
    ('other repayments, assumed mid-quarter', -(256011 - 180000) * YIELD_DEBT * d(46)),
    ('new first lien loans, assumed mid-quarter', 28176 * YIELD_DEBT * d(46)),
]
slfp_common = (den * slfp_yield - I['slfp_notes'] * (max(sofr, 0.01) + 0.0475) - I['slfp_pref_liquidation'] * SLFP_PREF_RATE - den * SLFP_EXPENSES) / 4
steps.append(('SLFP common distributions (estimate)', slfp_common))
steps.append(('lower base fee on a smaller book', 5737 - 0.015 / 4 * I['investments_fv_ex_short_term']))
run = start
for n, v in steps:
    run += v
    print(f"  {n:58s} {v:+8,.0f}k")
fee = incentive_fee(run, I['net_assets_2026_09_30'], I)
print(f"run-rate quarter without Longview: pre-incentive {run:,.0f}k, fee {fee:,.0f}k, NII {run-fee:,.0f}k = ${(run-fee)/sh:.3f}/share vs $0.25 declared for Q1 2027")
gap = 0.25 * sh - (run - fee)
print(f"gap to a $0.25 distribution: {gap:,.0f}k a quarter, {gap*4:,.0f}k a year")

# What the Longview cash can do once AEP closes (assumes CION gets the 30 Sep mark in cash)
lv = 99241
px = I['price_2026_11_13']
na = I['net_assets_2026_09_30']
net_debt = I['debt_principal'] - I['cash'] - I['short_term_investments'] - lv
cap = I['leverage_target_high']
buy = (cap * na - net_debt) / (1 + cap)          # buyback that takes net debt/equity back to 1.35x
buy = min(buy, I['buyback_authorization_remaining'], lv)
shares_bought = buy / px
rest = lv - buy
nii_a = run + rest * (sofr + 0.0475) / 4         # rest repays the SOFR+4.75% Tranche A notes
na_a = na - buy
fee_a = incentive_fee(nii_a, na_a, I)
sh_a = sh - shares_bought
print(f"Longview cash {lv:,.0f}k: buyback room at {cap}x net leverage = {buy:,.0f}k = {shares_bought:,.0f}k shares at ${px}, the rest {rest:,.0f}k repays Tranche A")
print(f"  NAV/share after buyback ${na_a/sh_a:.2f} (from ${na/sh:.2f}); quarterly NII ${(nii_a-fee_a)/sh_a:.3f}/share")
nii_b = run + lv * (YIELD_DEBT - 0.015) / 4      # all reinvested in loans, less the base fee
fee_b = incentive_fee(nii_b, na, I)
print(f"  if instead all of it goes back into loans: NII ${(nii_b-fee_b)/sh:.3f}/share")
