# Value per share from the buckets in book_quality.py. This is now my cross-check; the target
# itself comes from nav_model.py. Every recovery below is my
# judgment, written down so you can change it. David's Bridal is tied to the Pearl terms
# (pearl_and_davids_bridal.py): base = deal closes, full redemptions, Pearl at $6.
from collections import defaultdict
from common import inputs, rows
import book_quality as bq

I = inputs()
sh = I['shares_outstanding_2026_09_30'] / 1000
px = I['price_2026_11_13']
mark = {k: v[1] for k, v in bq.B.items()}
other = I['cash'] + I['short_term_investments'] + I['interest_fees_receivable'] + I['receivable_investments_sold'] + I['prepaid_other']
R = {  # bucket: (bear, base, bull) share of the 30 Sep mark
    'Debt paying cash':     (0.93, 0.97, 1.00),
    # base from pik_cross_marks.py: loans other lenders also hold at their marks (92% of CION's),
    # everything else at 75%, blended 79%
    'Debt with PIK':        (0.55, 0.79, 0.90),
    'Debt on non-accrual':  (0.50, 0.90, 1.00),
    'Other equity':         (0.35, 0.60, 0.90),
    'Joint venture common': (0.50, 0.85, 1.00),
    "David's Bridal":       (0.40, 0.84, 1.00),
    # Longview from plant_dcf.py: bear = low case (power back to 2023-24 levels, capacity $150,
    # retire 2035), 41% of CION's mark; base = 80%; bull = power stays at EIA's 2027 forecast, 154%
    'Longview':             (0.41, 0.80, 1.54),
}
W = (0.35, 0.45, 0.20)
vals = []
print()
for i, n in enumerate(('bear', 'base', 'bull')):
    v = sum(mark[k] * R[k][i] for k in R) + other - I['total_liabilities']
    vals.append(v / sh)
    loss = I['net_assets_2026_09_30'] - v
    print(f"{n}: ${v/sh:.2f}/share ({v/sh/px-1:+.0%}); write-downs vs 30 Sep NAV {loss:,.0f}k = {loss/113671:.1f}x CION's 2025 net losses of 113,671k")
tgt = sum(w * v for w, v in zip(W, vals))
print(f"weighted (35/45/20): ${tgt:.2f}/share, {tgt/px-1:+.1%} vs ${px}; even weights ${sum(vals)/3:.2f}")
print(f"Buy line ${tgt/1.15:.2f}, Sell line ${tgt/0.85:.2f}")
# from 13 Nov (the day it went ex $0.10): about $1.00 over the next 12 months if $0.25 a quarter holds
fwd = 1.00
print(f"plus 12 months of distributions if $0.25 holds (${fwd:.2f}): ${tgt+fwd:.2f} ({(tgt+fwd)/px-1:+.0%} total)")
for k in ('Debt with PIK', "David's Bridal", 'Other equity'):
    print(f"sensitivity: 10 points on {k} = ${mark[k]*0.10/sh:.2f}/share")
print("moving each bucket from base to bear, one at a time:")
for k in sorted(R, key=lambda k: -mark[k] * (R[k][1] - R[k][0])):
    print(f"  {k}: ${mark[k]*(R[k][1]-R[k][0])/sh:.2f}/share")
# the weights are my judgment. Weighting instead by the last seven quarters' credit losses
# (nav_model.py: 4 at the bear pace or worse, 3 at the base pace or better; I count those 3 as 1 base and 2 bull, which is generous)
hw = (4 / 7, 1 / 7, 2 / 7)
print(f"weighted by the last seven quarters (4/1/2): ${sum(w * v for w, v in zip(hw, vals)):.2f}")

# what each case leaves for CION's unsecured notes: the UBS facility ($100m) is the only secured debt
secured = 100000
for n, v in zip(('bear', 'base', 'bull'), vals):
    eq = v * sh
    assets = eq + I['debt_principal']
    print(f"{n}: assets left for debt ~{assets:,.0f}k; after the secured facility, unsecured debt covered {(assets-secured)/(I['debt_principal']-secured):.2f}x")
