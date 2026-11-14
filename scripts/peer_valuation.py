# Is 0.47x NAV cheap for CION's book? Compare listed BDCs' price to NAV with how much of their
# payout was earned outside PIK, and with PIK as a share of investment income.
# Peers: every listed BDC with comparable nine-month 2026 data in my panel, plus BXSL and TSLX
# from their 10-Qs.
from common import rows
import statistics as st

P = rows('peer_bdcs_2026_09.csv')
for r in P:
    for k in ('nav_per_share_2026_09_30', 'price_2026_11_13', 'nii_9m', 'pik_9m', 'total_investment_income_9m', 'distributions_9m'):
        r[k] = float(r[k])
    r['pnav'] = r['price_2026_11_13'] / r['nav_per_share_2026_09_30']
    r['expik'] = (r['nii_9m'] - r['pik_9m']) / r['distributions_9m']
    r['pik_share'] = r['pik_9m'] / r['total_investment_income_9m']

def ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    r2 = 1 - sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / sum((y - my) ** 2 for y in ys)
    return a, b, r2

for r in sorted(P, key=lambda r: r['pnav']):
    print(f"  {r['ticker']:5s} P/NAV {r['pnav']:.2f}   NII ex-PIK cover {r['expik']:.2f}   PIK {r['pik_share']:.0%} of investment income")
peers = [r for r in P if r['ticker'] != 'CION']
c = [r for r in P if r['ticker'] == 'CION'][0]
print(f"\n{len(peers)} peers, median P/NAV {st.median(r['pnav'] for r in peers):.2f}")
for key, label in (('pik_share', 'PIK share of investment income'), ('expik', 'NII ex-PIK coverage')):
    a, b, r2 = ols([r[key] for r in peers], [r['pnav'] for r in peers])
    fit = a + b * c[key]
    print(f"P/NAV on {label}: slope {b:.2f}, R-squared {r2:.2f}; at CION's {c[key]:.2f} the fit says {fit:.2f}x = ${fit*c['nav_per_share_2026_09_30']:.2f}"
          f" (CION's value is outside the peers' range, so this is an extrapolation)")
low = min(peers, key=lambda r: r['expik'])
print(f"nearest peer on ex-PIK coverage: {low['ticker']} at {low['expik']:.2f}x trades at {low['pnav']:.2f}x NAV; CION at {c['expik']:.2f}x trades at {c['pnav']:.2f}x")
