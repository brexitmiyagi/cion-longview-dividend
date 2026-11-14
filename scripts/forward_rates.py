# My base case used to hold SOFR flat at about 3.90%. The futures market doesn't: on 13 Nov 2026
# three-month SOFR futures priced SOFR rising to about 4.8% by late 2027. nav_model.py now runs
# on that curve (common.curve_add). This prints the curve and the flat-rate version next to it.
import io, os, runpy, contextlib, datetime as dt
from common import rows

HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
run = M['run']; I = M['I']
BASE_10Q = 0.0388

F = rows('sofr_futures_2026_11_13.csv')
pts = []
for r in F:
    start = dt.date.fromisoformat(r['reference_quarter_start'])
    pts.append((start + dt.timedelta(days=45), (100 - float(r['last_2026_11_13'])) / 100))
def sofr_on(d):
    for (d0, r0), (d1, r1) in zip(pts, pts[1:]):
        if d0 <= d <= d1:
            return r0 + (r1 - r0) * (d - d0).days / (d1 - d0).days
    raise ValueError(d)
MID = {'Q4 2026': dt.date(2026, 11, 15), 'Q1 2027': dt.date(2027, 2, 14), 'Q2 2027': dt.date(2027, 5, 16),
       'Q3 2027': dt.date(2027, 8, 15), 'Q4 2027': dt.date(2027, 11, 15)}
PATH = {q: sofr_on(d) for q, d in MID.items()}

T = sorted([(0, 0.0)] + [(int(r['change_bp']), float(r['net_interest_income_change_k'])) for r in rows('rate_sensitivity_2026_09_30.csv')])
def nii_change(bp):
    for (b0, v0), (b1, v1) in zip(T, T[1:]):
        if b0 <= bp <= b1:
            return v0 + (v1 - v0) * (bp - b0) / (b1 - b0)
    raise ValueError(bp)
ADD = {q: nii_change((r - BASE_10Q) * 1e4) / 4 for q, r in PATH.items()}

print("SOFR futures, 13 Nov 2026 (CME last; Yahoo close as a check):")
for r in F:
    y = f", Yahoo {r['yahoo_close_2026_11_13']}" if r['yahoo_close_2026_11_13'] else ''
    print(f"  {r['globex']} from {r['reference_quarter_start']}: {r['last_2026_11_13']} = {100-float(r['last_2026_11_13']):.3f}%{y}")
print("quarterly SOFR on the curve, shift from the 10-Q's 3.88%, and what it adds to NII before fees:")
for q in MID:
    print(f"  {q}: {PATH[q]:.2%}  {(PATH[q]-BASE_10Q)*1e4:+.0f}bp  {ADD[q]:+,.0f}k")

sh0 = I['shares_outstanding_2026_09_30'] / 1000
out = {}
for case in ('bear', 'base', 'bull'):
    flat = run(case, rate_add={}); fwd = run(case)
    out[case] = fwd
    print(f"{case}:")
    for a, b in zip(flat, fwd):
        print(f"  {a['q']}: NII flat ${a['nii_ps']:.3f}, on the curve ${b['nii_ps']:.3f}; NAV/share ${b['nav_ps']:.2f}")
    print(f"  2027 NII: flat ${sum(x['nii_ps'] for x in flat[1:]):.2f}, on the curve ${sum(x['nii_ps'] for x in fwd[1:]):.2f}")
b = out['base']
cov = [x['nii_ps'] / x['dist_ps'] for x in b[2:]]
print(f"base on the curve, coverage after the sale: {min(cov):.2f}x to {max(cov):.2f}x")


# Is the curve on its own? Fed funds futures and Treasury bills on the same day point the same
# way: the market expects the Fed to raise rates by about 3/4 to 1 point through 2027.
X = {(r['series'], r['month_or_tenor']): float(r['value']) for r in rows('rates_crosscheck_2026_11_13.csv')}
eff = X[('effective_fed_funds', '12 Nov 2026')]
print(f"fed funds futures, 13 Nov 2026 (effective fed funds {eff:.2f}% on 12 Nov): " + ", ".join(
    f"{m} {100-X[('fed_funds_futures', m)]:.2f}%" for m in ('Dec 2026', 'Mar 2027', 'Jun 2027', 'Sep 2027', 'Dec 2027')))
print(f"  implied rise by Dec 2027: {(100-X[('fed_funds_futures','Dec 2027')]-eff)*100:.0f}bp; SOFR futures: {(PATH['Q4 2027']-0.0390)*1e4:.0f}bp")
print(f"Treasury bills: 3 months {X[('treasury_cmt','3 Mo')]:.2f}%, 6 months {X[('treasury_cmt','6 Mo')]:.2f}%, 1 year {X[('treasury_cmt','1 Yr')]:.2f}%, against SOFR {X[('sofr','12 Nov 2026')]:.2f}%")
# The base for the shift: the 10-Q's rate table starts from 3.88%. The run-rate is built from Q3
# income, when SOFR averaged 3.67%, so measuring from 3.88% leaves out about 20bp of the lift.
q3 = X[('sofr_average', 'Q3 2026')] / 100
from common import nii_change_k
sh = I['shares_outstanding_2026_09_30'] / 1000
print(f"SOFR averaged {q3:.2%} in Q3 2026 against the 10-Q's 3.88% base: measuring from Q3 would add about {nii_change_k((0.0388-q3)*1e4)/sh*100:.1f} cents a year before the incentive fee, so my base is the cautious one")
