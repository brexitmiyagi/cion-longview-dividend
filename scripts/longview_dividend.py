# The power plant and the third quarter.
# Longview's quarterly dividend comes from the year-to-date column of the affiliated
# investments table in each 10-Q, so Q3 = nine months minus six months.
import os
from common import inputs, rows, incentive_fee

HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()
lv = rows('longview.csv')
fv = {r['period_end']: float(r['fair_value_k']) for r in lv}
ytd = {r['period_end']: float(r['dividend_income_ytd_k']) for r in lv if r['dividend_income_ytd_k']}
sh = I['shares_outstanding_2026_09_30'] / 1000  # thousands, to match the $k figures

q = {'Q1 2026': ytd['2026-03-31'], 'Q2 2026': ytd['2026-06-30'] - ytd['2026-03-31'], 'Q3 2026': ytd['2026-09-30'] - ytd['2026-06-30']}
print('Longview dividends to CION ($k): FY2025', ytd['2025-12-31'], '|', ', '.join(f'{k} {v:,.0f}' for k, v in q.items()))
q3 = q['Q3 2026']
print(f"Q3 Longview dividend {q3:,.0f}k = ${q3/sh:.3f}/share; all affiliated dividends in Q3 {I['q3_affiliated_dividend_income']:,.0f}k")
print(f"Q3 distributions paid {I['q3_distributions_paid']:,.0f}k; Longview covered {q3/I['q3_distributions_paid']:.0%} of them")

# What the plant was worth before and after it paid out
chg = fv['2026-09-30'] - fv['2026-06-30']
print(f"Longview mark 30 Jun {fv['2026-06-30']:,.0f}k -> 30 Sep {fv['2026-09-30']:,.0f}k ({chg:+,.0f}k); total return in Q3 = {q3+chg:,.0f}k")
print(f"Longview mark = {fv['2026-09-30']/I['net_assets_2026_09_30']:.1%} of net assets, ${fv['2026-09-30']/sh:.2f}/share, {fv['2026-09-30']/I['investments_fv_ex_short_term']:.1%} of the portfolio; cost {lv[-1]['cost_k']}k, mark is {fv['2026-09-30']/float(lv[-1]['cost_k']):.1f}x cost")
print(f"Cash dividends since start of 2025: {ytd['2025-12-31'] + ytd['2026-09-30']:,.0f}k")

# Net investment income without the plant. The incentive fee is 17.5% of all
# pre-incentive NII once it clears the catch-up, so take it out first.
pre = I['q3_nii_after_tax'] + I['q3_incentive_fee']
hurdle = I['hurdle_rate_quarterly'] * I['net_assets_2026_06_30']
print(f"pre-incentive NII {pre:,.0f}k; hurdle {hurdle:,.0f}k; fee recomputed {incentive_fee(pre, I['net_assets_2026_06_30'], I):,.0f}k vs reported {I['q3_incentive_fee']:,.0f}k")
ex = pre - q3
fee_ex = incentive_fee(ex, I['net_assets_2026_06_30'], I)
print(f"Q3 NII without Longview: {ex - fee_ex:,.0f}k = ${(ex-fee_ex)/sh:.3f}/share (below the hurdle, so no incentive fee)")
one_offs = I['q3_debt_cost_writeoff'] + I['q3_legacy_fee_reversal'] + (I['q3_professional_fees'] - I['q3_2025_professional_fees'])
adj = ex + one_offs
print(f"one-offs management named: debt cost write-off {I['q3_debt_cost_writeoff']:,.0f}k + legacy fee reversal {I['q3_legacy_fee_reversal']:,.0f}k + extra legal fees {I['q3_professional_fees']-I['q3_2025_professional_fees']:,.0f}k = {one_offs:,.0f}k")
print(f"Q3 NII without Longview, one-offs added back: {adj:,.0f}k = ${adj/sh:.3f}/share (hurdle {hurdle:,.0f}k, so still no incentive fee)")
# Management's count is bigger. On the call it put three items at roughly $0.15 a share, plus the
# $0.03 debt cost write-off. The third item, accrued income reversed on the Thrill One loan after
# its reorganisation, isn't quantified anywhere, so I back it out of the $0.15 as a residual. It's
# an income reversal on a loan that went bad, which is a credit cost. My NAV model already charges
# credit losses every quarter, so leaving it in the run-rate as well would count it twice. I now
# use management's count.
thrill = I['q3_mgmt_one_offs_per_share'] * sh - I['q3_legacy_fee_reversal'] - (I['q3_professional_fees'] - I['q3_2025_professional_fees'])
adj_m = adj + thrill
print(f"management's count: $0.15 of items plus the write-off; the Thrill One reversal by residual is about {thrill:,.0f}k")
print(f"Q3 NII without Longview on management's count: {adj_m:,.0f}k = ${adj_m/sh:.3f}/share (hurdle {hurdle:,.0f}k)")
print(f"PIK share of Q3 investment income: {I['q3_pik_income']/I['q3_total_investment_income']:.1%}")
