# What a move in rates does to my 2027 NII. The base case follows the SOFR futures curve of
# 13 Nov 2026 (common.curve_add). Here I shift the whole curve up or down in parallel and rerun
# the base case; the extra change in net interest income comes from the rate table in CION's
# 10-Q (data/rate_sensitivity_2026_09_30.csv), added before the incentive fee so the fee's
# catch-up is counted. The flat-rate line is what my earlier drafts used.
import io, os, runpy, contextlib
from common import curve_add, sofr_curve

HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
run = M['run']
fy = lambda r: sum(x['nii_ps'] for x in r[1:])
q3 = lambda r: [x for x in r if x['q'] == 'Q3 2027'][0]['nii_ps']
path = sofr_curve()
print("SOFR on the futures curve: " + ", ".join(f"{q} {v:.2%}" for q, v in path.items()))
print("curve shift | average 2027 SOFR | my 2027 NII | Q3 2027 NII | coverage of 25 cents, Q3 2027")
avg27 = sum(v for q, v in path.items() if q != 'Q4 2026') / 4
for bp in (-100, -50, 0, 50, 100):
    out = run('base', rate_add=curve_add(bp))
    print(f"  {bp:+5d}bp | {avg27 + bp/1e4:.2%} | ${fy(out):.2f} | ${q3(out):.3f} | {q3(out)/0.25:.2f}x")
flat = run('base', rate_add={})
print(f"  SOFR flat at about 3.9% (my earlier drafts): 2027 ${fy(flat):.2f}, Q3 2027 ${q3(flat):.3f}, {q3(flat)/0.25:.2f}x")
