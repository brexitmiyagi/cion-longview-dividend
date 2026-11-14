# Is CION booking interest it isn't collecting? PIK is added to the loan, so it doesn't show up
# here; this is cash interest that's due but not yet paid. If it grows faster than income, more of
# the earnings are accruals. It hasn't: the ratio peaked in 2024 and has come down.
from common import rows
R = rows('income_and_fees_quarterly.csv')
print("quarter     | interest receivable | quarter's investment income | ratio")
for r in R:
    rec = float(r['interest_receivable_end_k']); tii = float(r['total_investment_income_k'])
    print(f"  {r['quarter_end']}  {rec:9,.0f}k  {tii:9,.0f}k  {rec/tii:.2f}")
peak = max(R, key=lambda r: float(r['interest_receivable_end_k']))
print(f"peak {float(peak['interest_receivable_end_k']):,.0f}k at {peak['quarter_end']}; latest {float(R[-1]['interest_receivable_end_k']):,.0f}k")
