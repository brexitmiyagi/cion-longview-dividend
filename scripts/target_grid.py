# The two inputs that move my target most, side by side: what Longview sells for (as a share of
# CION's 30 Sep mark) and how much of today's discount to the peer line is still there in a year.
# 41% is my bear case, 55% is where Virtus and City National marked the same units on 30 Jun
# ($40.00 against CION's $72.74), 80% is my base case and 100% is CION's own mark. 79%, 93% and
# 100% are the low end, middle and high end of the persistence test (discount_persistence.py).
# Everything else is my base case.
import io, os, runpy, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
run, value, a1, b1, px = M['run'], M['value'], M['a1'], M['b1'], M['px']
CASES = M['run'].__globals__['CASES']
KEEP_LO, KEEP, KEEP_HI = M['KEEP_LO'], M['KEEP'], M['KEEP_HI']
third_party = 40.00 / 72.74
lv0 = CASES['base']['lv']
sale = [('41% (my bear)', 0.41), (f'{third_party:.0%} (other funds\' 30 Jun mark)', third_party),
        ('80% (my base)', 0.80), ('100% (CION\'s mark)', 1.00)]
keeps = [KEEP_LO, KEEP, KEEP_HI]
print('Longview sale price, % of mark | ' + ' | '.join(f'{k:.0%} of the gap kept' for k in keeps))
grid = {}
for lab, s in sale:
    CASES['base']['lv'] = s
    r = [x for x in run('base') if x['q'] == 'Q3 2027'][0]
    m = a1 + b1 * r['nii'] * 4 / r['na']
    vals = [value(m, r['nav_ps'], k) for k in keeps]
    grid[lab] = vals
    print(f'{lab} | ' + ' | '.join(f'${v:.2f} ({v/px-1:+.0%})' for v in vals))
CASES['base']['lv'] = lv0
allv = [v for vs in grid.values() for v in vs]
print(f'price ${px}; Sell below ${px*0.85:.2f}, Buy above ${px*1.15:.2f}; grid runs ${min(allv):.2f} to ${max(allv):.2f}')
print(f'cells that would be a Sell on price: {sum(v < px*0.85 for v in allv)} of {len(allv)}; a Buy: {sum(v > px*1.15 for v in allv)}')
