# What $6.19 says about the book, and what my scenarios say it is worth.
from common import inputs, rows

I = inputs()
sh = I['shares_outstanding_2026_09_30'] / 1000
px = I['price_2026_11_13']
na = I['net_assets_2026_09_30']
mcap = px * sh
print(f"price ${px} / NAV ${I['nav_per_share_2026_09_30']} = {px/I['nav_per_share_2026_09_30']:.2f}x; market cap {mcap:,.0f}k")
print(f"distribution yield at $0.25 a quarter: {1.00/px:.1%}")

lv = 99241
db = [r for r in rows('davids_bridal.csv') if r['period_end'] == '2026-09-30']
db_fv = sum(float(r['fair_value_k']) for r in db)
db_q2 = sum(float(r['fair_value_k']) for r in rows('davids_bridal.csv') if r['period_end'] == '2026-06-30')
eq = lambda p: sum(float(r['fair_value_k']) for r in rows('davids_bridal.csv') if r['period_end'] == p and r['par_k'] == '')
print(f"David's Bridal: {db_fv:,.0f}k at 30 Sep ({db_fv/na:.1%} of NAV), {db_q2:,.0f}k at 30 Jun; equity {eq('2026-06-30'):,.0f}k -> {eq('2026-09-30'):,.0f}k ({eq('2026-09-30')/eq('2026-06-30')-1:+.0%})")
two = lv + db_fv
print(f"Longview + David's Bridal = {two:,.0f}k = {two/na:.1%} of NAV = ${two/sh:.2f}/share; market cap / those two = {mcap/two:.2f}")

other_assets = I['cash'] + I['short_term_investments'] + I['interest_fees_receivable'] + I['receivable_investments_sold'] + I['prepaid_other']
implied_all = mcap + I['total_liabilities'] - other_assets
rest_fv = I['investments_fv_ex_short_term'] - two
implied_rest = implied_all - two
print(f"market-implied value of the whole portfolio: {implied_all:,.0f}k vs marks {I['investments_fv_ex_short_term']:,.0f}k = {implied_all/I['investments_fv_ex_short_term']:.1%}")
print(f"with Longview and David's Bridal at their marks, the rest ({rest_fv:,.0f}k) is priced at {implied_rest:,.0f}k = {implied_rest/rest_fv:.1%} of its marks")

print(f"what Longview alone is, per share, against the price: ${lv/sh:.2f} = {lv/sh/px:.0%} of ${px}")
mp_gap = I["investments_fv_ex_short_term"] - implied_all
print(f"the write-down the price implies: {mp_gap:,.0f}k = ${mp_gap/(I['shares_outstanding_2026_09_30']/1000):.2f} a share")
