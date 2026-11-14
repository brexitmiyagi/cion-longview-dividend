# What a CICB holder should look at: the $327.5 million of CION debt that comes due in 2027,
# against the cash CION can point at. Sources and uses, my base case (Longview at 80% of its
# mark, buybacks first, as management says). Loan repayments are the other source; I show what
# they ran at in 2026, without the one-off sale of $180 million of loans to the joint venture.
import io, os, runpy, contextlib
from common import inputs, rows
HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()
with contextlib.redirect_stdout(io.StringIO()):
    B = runpy.run_path(os.path.join(HERE, 'core_earnings_bridge.py'))
D = [r for r in rows('debt_2026_09_30.csv') if r['maturity'].startswith('2027')]
due = sum(float(r['amount_k']) for r in D)
print("due in 2027:")
for r in sorted(D, key=lambda r: r['maturity']):
    print(f"  {r['maturity']}  {r['facility']:38s} {float(r['amount_k']):>9,.0f}k")
print(f"  total {due:,.0f}k")
cash = I['cash'] + I['short_term_investments']; undrawn = 25000
lv = 99241 * 0.80; buy = B['buy']
src = [('cash and short-term investments, 30 Sep 2026', cash), ('undrawn on the UBS facility', undrawn),
       ('Longview at 80% of its mark, less buybacks first', lv - buy)]
tot = sum(v for _, v in src)
print("sources I can point at:")
for k, v in src:
    print(f"  {k}: {v:,.0f}k")
print(f"  total {tot:,.0f}k; left to refinance or pay from loan repayments: {due - tot:,.0f}k ({(due-tot)/due:.0%})")
L = {r['period']: r for r in rows('peer_level3_9m.csv') if r['lender'] == 'CION'}
ex26 = float(L['9M 2026']['exits']) - I['slfp_loans_sold_price']
print(f"loan repayments and sales, nine months of 2026 without the joint-venture sale: {ex26:,.0f}k, about {ex26/3:,.0f}k a quarter")
print(f"  the gap is about {(due-tot)/(ex26/3):.1f} quarters of that, if CION shrinks instead of refinancing")
