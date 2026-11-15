# From Q3 2026's 1.5 cents of NII without Longview to my 21.4 cent run-rate quarter, in one
# column. Levels are printed in cents to one decimal and each step is the difference between the
# rounded levels, so the column adds up as printed. Rates are flat here; the futures curve adds
# a little on top from Q4 (nav_model.py).
import io, os, runpy, contextlib
from common import inputs
HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()
with contextlib.redirect_stdout(io.StringIO()):
    LD = runpy.run_path(os.path.join(HERE, 'longview_dividend.py'))
    B = runpy.run_path(os.path.join(HERE, 'core_earnings_bridge.py'))
sh = I['shares_outstanding_2026_09_30'] / 1000
lv_ex = LD['ex'] - LD['fee_ex']
levels = [
    ("Q3 2026 NII without Longview's dividend", lv_ex),
    ("add back the one-offs management named: the debt write-off, the reversed fee and the extra legal costs", LD['adj']),
    ("add back the income reversed on the reorganized loan (management's rounded count)", LD['adj_m']),
    ("roll forward to today's balance sheet: debt repaid, loans moved to the joint venture, new loans", B['run'] - B['fee_base']),
    ("fee income at Q3's lending pace and the 2023-2025 fee rate", B['run']),
    ("less the adviser's income incentive fee", B['run'] - B['fee']),
]
prev = None
for lab, v in levels:
    c = round(v / sh * 100, 1)
    print(f"  {c:5.1f} cents" + (f"  ({c - prev:+.1f})" if prev is not None else '         ') + f"  {lab}")
    prev = c

# Where the run-rate sits against the fee. Between 1.625% and 1.970% of net assets a quarter
# (the catch-up) the adviser takes every extra dollar, so NII without Longview is stuck at the
# hurdle until pre-incentive income gets past the top of that band.
from common import incentive_fee, curve_add
na = I['net_assets_2026_09_30']; lo = I['hurdle_rate_quarterly'] * na; hi = 0.0197 * na
pre = B['run']; cv = curve_add()
print(f"catch-up band on 30 Sep net assets: {lo:,.0f}k to {hi:,.0f}k of pre-incentive NII a quarter")
for q in ('Q4 2026', 'Q1 2027'):
    p = pre + cv[q]
    print(f"  {q} without Longview, on the futures curve: pre-incentive {p:,.0f}k, fee {incentive_fee(p, na, I):,.0f}k, NII {p - incentive_fee(p, na, I):,.0f}k = {(p - incentive_fee(p, na, I))/sh*100:.1f} cents")

# How big a Longview dividend would lift Q4's headline NII to 25 cents, given the fee above.
for lab, add in (('flat rates', 0.0), ('futures curve', cv['Q4 2026'])):
    x = 0.0
    while True:
        p = pre + add + x
        if (p - incentive_fee(p, na, I)) / sh >= 0.25:
            break
        x += 10
    print(f"Longview dividend that lifts Q4 2026 headline NII to 25 cents ({lab}): about {x:,.0f}k")
