# What the buybacks do. Management says resuming buybacks is its first priority for the Longview
# cash. My base case buys back stock up to 1.35x net leverage at today's price and uses the rest to
# repay the SOFR+4.75% notes. Here's the same case with all the cash repaying notes instead.
import io, os, runpy, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
run = M['run']; G = run.__globals__; I = G['I']
q = lambda res, k: [x for x in res if x['q'] == k][0]
base = run('base')
keep = I['buyback_authorization_remaining']; I['buyback_authorization_remaining'] = 0.0
nob = run('base'); I['buyback_authorization_remaining'] = keep
for lab, r in (('with buybacks (base)', base), ('no buybacks, all cash to the notes', nob)):
    s = q(r, 'Q3 2027')
    print(f"  {lab}: Sep 2027 NAV ${s['nav_ps']:.2f}, shares {s['sh']/1000:.1f}m, Q3 2027 NII ${s['nii_ps']:.3f}")
d = q(base, 'Q3 2027')['nav_ps'] - q(nob, 'Q3 2027')['nav_ps']
print(f"buybacks add ${d:.2f} a share to NAV by Sep 2027 ({d/q(nob,'Q3 2027')['nav_ps']:.1%}); remaining authorization {keep:,.0f}k")
