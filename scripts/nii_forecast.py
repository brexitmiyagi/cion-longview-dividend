# Four quarters of NII per share, Q4 2026 to Q3 2027, against the distribution and the
# two-analyst consensus on Seeking Alpha. Everything here is my estimate.
#
# Start: the run-rate quarter without Longview from core_earnings_bridge.py, held flat (no
# growth, no new credit losses, no fee income, which was negative in Q3).
# Longview: it keeps paying dividends until AEP closes, and nobody outside knows how much.
# CION got 2.99m, 2.24m and 14.21m in the first three quarters of 2026. I use the average of
# the first two as my base, with nothing and the Q3 amount as the range.
# Closing: I assume the end of Q1 2027, the back end of AEP's window, and that CION gets its
# 30 Sep mark in cash. After that, either the cash sits earning about SOFR, or it goes half
# to work in Q2 and fully in Q3 the way core_earnings_bridge.py lays out (buyback to 1.35x net
# leverage, the rest repays the SOFR+4.75% Tranche A notes).
import io, os, runpy, contextlib
from common import inputs, rows, incentive_fee

HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()
with contextlib.redirect_stdout(io.StringIO()):
    B = runpy.run_path(os.path.join(HERE, 'core_earnings_bridge.py'))
core = B['run']                     # pre-incentive, thousands, per quarter
sh0 = I['shares_outstanding_2026_09_30'] / 1000
na0 = I['net_assets_2026_09_30']
sofr = I['sofr_3m_2026_09_30']
lv = 99241
lv_div = {'none': 0.0,
          'H1 2026 average': (I['longview_dividend_q1_2026'] + I['longview_dividend_q2_2026']) / 2,
          'Q3 2026 again': I['longview_dividend_q3_2026']}
fees = (I['fee_income_q1_2026'] + I['fee_income_q2_2026']) / 2
cons = {r['period']: float(r['nii_per_share_consensus']) for r in rows('consensus_2026_11_13.csv')}
dist = {'Q4 2026': 0.30, 'Q1 2027': 0.25, 'Q2 2027': 0.25, 'Q3 2027': 0.25}

def nii(pre, na, sh):
    return (pre - incentive_fee(pre, na, I)) / sh

def quarter(q, case='H1 2026 average', redeploy=False, extra=0.0):
    if q in ('Q4 2026', 'Q1 2027'):
        return nii(core + lv_div[case] + extra, na0, sh0)
    if not redeploy:
        return nii(core + lv * sofr / 4 + extra, na0, sh0)
    share = 0.5 if q == 'Q2 2027' else 1.0
    buy = B['buy'] * share; rest = B['rest'] * share
    pre = core + rest * (sofr + 0.0475) / 4 + (lv - buy - rest) * sofr / 4 + extra
    return nii(pre, na0 - buy, sh0 - buy / I['price_2026_11_13'])

print(f"run-rate pre-incentive NII without Longview (core_earnings_bridge.py): {core:,.0f}k = ${core/sh0:.3f}/share")
print()
print("quarter  | distribution | consensus | mine, cash not redeployed | mine, redeployed | coverage (not / redeployed)")
tot_a = tot_b = 0.0
for q in dist:
    a = quarter(q); b = quarter(q, redeploy=True)
    tot_a += a; tot_b += b
    c = f"${cons[q]:.2f}" if q in cons else '  -  '
    print(f"  {q}  ${dist[q]:.2f}         {c}      ${a:.3f}                     ${b:.3f}            {a/dist[q]:.2f}x / {b/dist[q]:.2f}x")
print(f"  four quarters: distributions ${sum(dist.values()):.2f}; mine ${tot_a:.2f} not redeployed, ${tot_b:.2f} redeployed")
print()
print("Longview dividend before closing (Q4 2026 and Q1 2027):")
for k in lv_div:
    print(f"  {k} ({lv_div[k]:,.0f}k a quarter): ${quarter('Q4 2026', k):.3f}/share")
print(f"what Longview would have to pay in Q4 for my numbers to reach the ${cons['Q4 2026']:.2f} consensus: ", end='')
lo, hi = 0.0, 40000.0
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if nii(core + m, na0, sh0) < cons['Q4 2026'] else (lo, m)
print(f"about {m:,.0f}k")
print()
print(f"if fee income comes back to its first-half 2026 average ({fees:,.0f}k a quarter):")
for q in dist:
    print(f"  {q}: ${quarter(q, extra=fees):.3f} not redeployed, ${quarter(q, redeploy=True, extra=fees):.3f} redeployed")
print()
print(f"consensus for FY2027 is ${cons['FY 2027']:.2f}, ${cons['FY 2027']/4:.3f} a quarter; my Q3 2027 redeployed with fees back is ${quarter('Q3 2027', redeploy=True, extra=fees):.3f}")
