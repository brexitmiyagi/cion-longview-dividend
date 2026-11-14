# The Q3 one-offs I add back, counted two ways, and what each does to 2027 and the target.
# Management's count: "roughly $0.15 per share" of items plus the $0.03 debt write-off, with the
# Thrill One income reversal backed out as a residual (longview_dividend.py). My narrower count
# leaves that reversal in the run-rate. Both rows use my base-case fee income.
import io, os, runpy, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
    LD = runpy.run_path(os.path.join(HERE, 'longview_dividend.py'))
run = M['run']; G = run.__globals__; core0 = G['core']
a1, b1, pik_q, px, blend = M['a1'], M['b1'], M['pik_q'], M['px'], M['blend']
def show(lab, c):
    G['core'] = c
    b = run('base'); r = [x for x in b if x['q'] == 'Q3 2027'][0]
    roe = (r['nii'] - pik_q * 0.21) * 4 / r['na']; t = blend(a1 + b1 * roe, r['na'] / r['sh'])
    print(f"  {lab}: Q4 2026 ${b[0]['nii_ps']:.2f}, 2027 ${sum(x['nii_ps'] for x in b[1:]):.2f}, target ${t:.2f} ({t/px-1:+.0%})")
print(f"Thrill One reversal by residual: {LD['thrill']:,.0f}k = ${LD['thrill']/(M['I']['shares_outstanding_2026_09_30']/1000):.3f} a share")
show("management's count (base case)", core0)
show("my narrower count", core0 - LD['thrill'])
G['core'] = core0
