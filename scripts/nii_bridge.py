# From my Q3 2027 NII to the consensus, one change at a time. Q3 2027 is the first full quarter
# after AEP closes (I assume the end of Q1 2027). Each line reruns nav_model.py's base case with
# one more assumption switched to the friendliest version I think is defensible, so the steps
# add up. Whatever is left at the end is the part of the consensus I can't explain.
import io, os, runpy, contextlib
from common import inputs, rows

HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
run = M['run']; G = run.__globals__
cons = {r['period']: float(r['nii_per_share_consensus']) for r in rows('consensus_2026_11_13.csv')}
sh0 = I['shares_outstanding_2026_09_30'] / 1000
fees = (I['fee_income_q1_2026'] + I['fee_income_q2_2026']) / 2

def q3():
    return [x for x in run('base') if x['q'] == 'Q3 2027'][0]['nii_ps']

core0, case0 = G['core'], dict(G['CASES']['base'])
steps = []
# the starting points
q1 = [x for x in run('base') if x['q'] == 'Q1 2027'][0]['nii_ps']
lvd = G['lv_div']
base = q3(); steps.append(('my base case, Q3 2027', base))
G['CASES']['base']['loss'] = 0.0; s = q3(); steps.append(('no credit losses at all from here', s))
G['CASES']['base']['lv'] = 1.0; s2 = q3(); steps.append(("Longview sells at CION's full mark, not 80%", s2))
G['core'] = core0 - G['B']['fee_base'] + fees; s3 = q3(); steps.append(('fee income back to its first-half 2026 average', s3))
G['core'] = core0; G['CASES']['base'].update(case0)

print(f"Q1 2027, the last quarter with Longview dividends (H1 2026 average, {lvd:,.0f}k): ${q1:.3f}")
print(f"  the Longview dividend alone is about ${lvd/sh0:.3f} a share before the incentive fee")
prev = None
for lab, v in steps:
    print(f"  {lab}: ${v:.3f}" + (f" ({v-prev:+.3f})" if prev is not None else ''))
    prev = v
c = cons['Q3 2027']
print(f"  consensus for Q3 2027: ${c:.2f}; not explained by anything above: ${c-prev:+.3f}")
print(f"  for 2027 as a whole: mine ${sum(x['nii_ps'] for x in run('base')[1:]):.2f}, consensus ${cons['FY 2027']:.2f}")
