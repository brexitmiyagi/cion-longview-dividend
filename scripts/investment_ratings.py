# CION grades every investment 1 to 5 each quarter (1 = better than at purchase, 2 = as expected,
# 3 = risk to cost has risen, 4 and 5 = loss of income or principal expected). The 10-Q gives the
# fair value in each grade. data/cion_investment_ratings.csv has eleven quarter-ends, Mar 2024 to
# Sep 2026, transcribed from each 10-Q and 10-K. Grades 3 to 5 are the watch list.
from common import rows
R = rows('cion_investment_ratings.csv')
print("quarter    | grade 1 | grade 2 | grade 3 | grades 4-5 | watch list (3-5)")
for r in R:
    v = [float(r[f'rating_{i}_fv_k']) for i in range(1, 6)]; t = float(r['total_fv_k'])
    print(f"{r['quarter_end']} | {v[0]/t:6.1%} | {v[1]/t:6.1%} | {v[2]/t:6.1%} | {(v[3]+v[4])/t:6.1%}   | {sum(v[2:]):>9,.0f}k = {sum(v[2:])/t:.1%}")
first, last = R[0], R[-1]
w = lambda r: sum(float(r[f'rating_{i}_fv_k']) for i in (3, 4, 5))
hi = max(R[:-1], key=lambda r: w(r) / float(r['total_fv_k']))
print(f"watch list on 30 Sep 2026: {w(last):,.0f}k, {w(last)/float(last['total_fv_k']):.1%} of the portfolio, the highest of the eleven quarters "
      f"(previous high {w(hi)/float(hi['total_fv_k']):.1%} on {hi['quarter_end']})")
prev = R[-2]
print(f"Q3 2026: watch list {w(prev):,.0f}k -> {w(last):,.0f}k ({w(last)-w(prev):+,.0f}k) while the portfolio fell {float(prev['total_fv_k']):,.0f}k -> {float(last['total_fv_k']):,.0f}k;"
      f" grade 2 fell {float(prev['rating_2_fv_k'])-float(last['rating_2_fv_k']):,.0f}k (the loans sold to SLFP were graded well, see jv_forensics.py)")
