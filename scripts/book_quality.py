# Sort every position in the 30 Sep 2026 schedule into buckets, then ask what price the
# market is putting on the riskier ones if the cash-pay loans are worth their marks.
import csv, os
from collections import defaultdict
from common import inputs, rows

I = inputs()
S = rows('schedule_2026_09_30.csv')

def bucket(r):
    n, f, sec = r['name'], r['footnotes'], r['section']
    if 'Longview' in n: return 'Longview'
    if "David's Bridal" in n: return "David's Bridal"
    if 'Senior Loan Fund' in n: return 'Joint venture common'
    if sec in ('FL', '2L', 'UNS'):
        if 'q' in f: return 'Debt on non-accrual'
        if 't' in f: return 'Debt with PIK'
        return 'Debt paying cash'
    return 'Other equity'

B = defaultdict(lambda: [0.0, 0.0, 0])
for r in S:
    b = B[bucket(r)]; b[0] += float(r['cost_k']); b[1] += float(r['fair_value_k']); b[2] += 1
tot = sum(v[1] for v in B.values())
print(f"portfolio at fair value {tot:,.0f}k (release: {I['investments_fv_ex_short_term']:,.0f}k)")
for k, (c, f, n) in sorted(B.items(), key=lambda x: -x[1][1]):
    print(f"  {k:24s} {n:3d} positions  cost {c:>9,.0f}k  mark {f:>9,.0f}k  ({f/c:.0%} of cost, {f/tot:.1%} of portfolio)")
past = [r for r in S if 'x' in r['footnotes']]
print(f"loans past maturity still carried (footnote x): {len(past)}, mark {sum(float(r['fair_value_k']) for r in past):,.0f}k")
law = sum(float(r['fair_value_k']) for r in S if 'Hilliard' in r['name'] or 'Trammell' in r['name'])
print(f"loans to plaintiff law firms (Hilliard, Trammell): {law:,.0f}k, all PIK")

sh = I['shares_outstanding_2026_09_30'] / 1000
mcap = I['price_2026_11_13'] * sh
other = I['cash'] + I['short_term_investments'] + I['interest_fees_receivable'] + I['receivable_investments_sold'] + I['prepaid_other']
implied_all = mcap + I['total_liabilities'] - other
fixed = B['Longview'][1] + B["David's Bridal"][1] + B['Debt paying cash'][1]
risky = sum(B[k][1] for k in ('Debt with PIK', 'Debt on non-accrual', 'Other equity', 'Joint venture common'))
print(f"if Longview, David's Bridal and the cash-pay loans are worth their marks ({fixed:,.0f}k), the market prices the other {risky:,.0f}k"
      f" at {implied_all - fixed:,.0f}k = {(implied_all - fixed)/risky:.0%} of marks")
P = rows('pik_terms_2026_09_30.csv')
full = {r['portfolio_company'] for r in P if r['cash_rate'] == '—'}
part = {r['portfolio_company'] for r in P if r['cash_rate'] != '—'}
fp = sum(float(r['fair_value_k']) for r in S if bucket(r) == 'Debt with PIK' and r['name'] in full and r['name'] not in part)
print(f"PIK debt paying no cash at all (no cash rate in the PIK table): {fp:,.0f}k = {fp/I['net_assets_2026_09_30']:.0%} of NAV, {fp/tot:.1%} of the portfolio")
hc = sum(float(r['fair_value_k']) for r in S if 'Homer City' in r['name'])
print(f"Homer City Generation PIK notes: {hc:,.0f}k")
