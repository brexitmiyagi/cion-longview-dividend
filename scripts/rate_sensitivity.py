# What a move in base rates does to my 2027 NII. CION's 10-Q gives the change in net interest
# income over twelve months for parallel moves in rates, on the 30 Sep 2026 portfolio and debt
# (data/rate_sensitivity_2026_09_30.csv). My model holds SOFR flat; overnight SOFR was 3.90% on
# 12 Nov 2026 (FRED), about where it was on 30 Sep. Here I take the 10-Q's annual figure, spread
# it evenly over the quarters, add it to my run-rate before the incentive fee and rerun the base
# case, so the fee's catch-up is counted.
import io, os, runpy, contextlib
from common import rows

HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
run = M['run']; G = run.__globals__; core0 = G['core']
sh = M['I']['shares_outstanding_2026_09_30'] / 1000
base = run('base')
fy = lambda r: sum(x['nii_ps'] for x in r[1:])
q3 = lambda r: [x for x in r if x['q'] == 'Q3 2027'][0]['nii_ps']
print(f"base case: 2027 NII ${fy(base):.2f}, Q3 2027 ${q3(base):.3f}")
print("rate move | 10-Q: net interest income, 12 months | per share before fees | my 2027 NII | Q3 2027")
for r in rows('rate_sensitivity_2026_09_30.csv'):
    d = float(r['net_interest_income_change_k'])
    if abs(int(r['change_bp'])) > 100: continue
    G['core'] = core0 + d / 4
    out = run('base')
    print(f"  {int(r['change_bp']):+5d}bp | {d:+9,.0f}k ({float(r['pct_change']):+.1f}%) | {d/sh:+.3f} | ${fy(out):.2f} | ${q3(out):.3f}")
G['core'] = core0
