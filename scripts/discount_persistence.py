# How much of a BDC's discount to the peer price-to-NAV line is still there a year later?
# That's the weight question in nav_model.py: the target puts some weight on the line and the
# rest on today's discount carrying forward. If discounts close fully within a year, all the
# weight belongs on the line; if they don't move, none of it does.
#
# Data: data/bdc_discount_panel.csv (pull_discount_panel.py): the 16 peers in the line plus CION,
# quarter-ends Q4 2023 to Q3 2026, NAV and NII from SEC XBRL, price about six weeks after each
# quarter end. Each quarter I fit the same line as nav_model.py (P/NAV on annualised NII over net
# assets, NII averaged over the last three quarters, Hercules and Rand left out) and take each
# BDC's distance from it. Then I compare that distance with the same BDC's distance four quarters
# later. The slope of later on earlier is the share of the gap that's still there.
import numpy as np
from common import rows

P = rows('bdc_discount_panel.csv')
QE = sorted({r['quarter_end'] for r in P})
D = {(r['ticker'], r['quarter_end']): r for r in P}
TK = sorted({r['ticker'] for r in P})

def resid_table(q):
    i = QE.index(q)
    if i < 2:
        return None
    pts = {}
    for t in TK:
        r = D[(t, q)]
        nii3 = sum(float(D[(t, QE[j])]['nii_quarter']) for j in (i - 2, i - 1, i))
        roe = nii3 * 4 / 3 / float(r['net_assets'])
        pts[t] = (float(r['price']) / float(r['nav_per_share']), roe)
    peers = [t for t in pts if t != 'CION']
    X = np.array([[1, pts[t][1]] for t in peers]); y = np.array([pts[t][0] for t in peers])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {t: pts[t][0] - (coef[0] + coef[1] * pts[t][1]) for t in pts}, coef

RES = {q: resid_table(q) for q in QE}
pairs = []; cion = []
for i, q in enumerate(QE):
    if RES[q] is None or i + 4 >= len(QE):
        continue
    a, _ = RES[q]; b, _ = RES[QE[i + 4]]
    for t in a:
        (cion if t == 'CION' else pairs).append((q, t, a[t], b[t]))
x = np.array([p[2] for p in pairs]); y = np.array([p[3] for p in pairs])
slope = (x @ y) / (x @ x)                       # through the origin: a gap of zero stays zero
X1 = np.column_stack([np.ones_like(x), x]); c1, *_ = np.linalg.lstsq(X1, y, rcond=None)
starts = sorted({p[0] for p in pairs})
print(f"{len(pairs)} peer pairs, start quarters {starts[0]} to {starts[-1]}, each compared with four quarters later")
print(f"share of the gap to the line still there a year later: {slope:.2f} (with an intercept: {c1[0]:+.3f} + {c1[1]:.2f} x)")
big = [p for p in pairs if p[2] <= -0.10]
kept = [p[3] / p[2] for p in big]
print(f"BDCs at least 0.10x below the line ({len(big)} cases): median share still there a year later {np.median(kept):.2f}; "
      f"the gap narrowed in {sum(1 for p in big if p[3] > p[2])} of {len(big)}")
# bootstrap by ticker, so one BDC's quarters move together
rng = np.random.default_rng(7); tks = sorted({p[1] for p in pairs}); bs = []
for _ in range(2000):
    pick = rng.choice(tks, len(tks))
    xs = np.concatenate([[p[2] for p in pairs if p[1] == t] for t in pick]); ys = np.concatenate([[p[3] for p in pairs if p[1] == t] for t in pick])
    bs.append((xs @ ys) / (xs @ xs))
lo, hi = np.percentile(bs, [10, 90])
print(f"80% range, resampling BDCs: {lo:.2f} to {hi:.2f}")
print("CION's own gap to the line, each quarter: " + ", ".join(f"{q} {RES[q][0]['CION']:+.2f}" for q in QE if RES[q]))
for q, t, a, b in cion:
    print(f"  CION {q}: {a:+.2f} -> {b:+.2f} four quarters later")
w = 1 - slope
print(f"implied weight on the line in a 12-month target: {w:.0%} (nav_model.py used 50%)")
