# The credit numbers a BDC reader looks for first, at 30 Sep 2026: non-accruals, leverage,
# asset coverage against the 150% floor, and when the debt comes due.
import os
from common import inputs, rows

HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()

# Non-accruals. The release gives the percentages; the schedule of investments flags each
# position (footnote q, "investment or a portion thereof"), so I add them up as a check.
na = [r for r in rows('schedule_2026_09_30.csv') if 'q' in r['footnotes']]
cost = sum(float(r['cost_k']) for r in na); fv = sum(float(r['fair_value_k']) for r in na)
port_fv = I['investments_fv_ex_short_term']
port_cost = I['investments_cost_incl_short_term'] - I['short_term_investments']
print(f"non-accruals, release: {I['nonaccrual_pct_cost']:.2%} of the portfolio at cost, {I['nonaccrual_pct_fv']:.2%} at fair value")
print(f"  schedule check: {len(na)} positions, cost {cost:,.0f}k ({cost/port_cost:.2%}), fair value {fv:,.0f}k ({fv/port_fv:.2%}), marked at {fv/cost:.0%} of cost")
for r in na:
    print(f"    {r['name']}: cost {float(r['cost_k']):,.0f}k, fair value {float(r['fair_value_k']):,.0f}k")

debt = I['debt_principal']; eq = I['net_assets_2026_09_30']; cash = I['cash'] + I['short_term_investments']
print(f"debt {debt:,.0f}k, net assets {eq:,.0f}k: gross debt/equity {debt/eq:.2f}x, net of cash and short-term investments {(debt-cash)/eq:.2f}x")
cov = (eq + debt) / debt
print(f"asset coverage {cov:.0%} against the 150% floor; NAV could fall {eq - 0.5*debt:,.0f}k ({(eq-0.5*debt)/eq:.0%}) before coverage hits 150%")

# Maturities, from the debt table in the 10-Q (data/debt_2026_09_30.csv)
D = rows('debt_2026_09_30.csv')
by = {}
for r in D:
    y = r['maturity'][:4]; by.setdefault(y, []).append(r)
print("maturities:")
for y in sorted(by):
    tot = sum(float(r['amount_k']) for r in by[y])
    print(f"  {y}: {tot:,.0f}k = " + ", ".join(f"{r['facility']} {float(r['amount_k']):,.0f}k" for r in by[y]))
