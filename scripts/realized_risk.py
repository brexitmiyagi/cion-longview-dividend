# What holding CION common and CICB has actually been like, from CICB's first trading day
# (9 Oct 2024) to 13 Nov 2026: total return with distributions and coupons reinvested on the
# ex-date, annualised volatility of daily returns, the worst peak-to-trough fall, and how each
# moved over the two distribution cut announcements. BIZD, the BDC ETF, for reference.
# Daily closes and ex-dates from Yahoo Finance (data/daily_prices_2024_2026.csv). The notes trade
# flat, so the close includes accrued interest and the price drops on the ex-date like a stock's.
import math
from common import rows

R = rows('daily_prices_2024_2026.csv')
def series(px, dv):
    out = []; idx = 1.0; prev = None
    for r in R:
        if not r[px]:
            continue
        p = float(r[px]); d = float(r[dv]) if r[dv] else 0.0
        if prev is not None:
            idx *= (p + d) / prev
        out.append((r['date'], p, idx)); prev = p
    return out
S = {'CION common': series('cion_close', 'cion_distribution_ex'), 'CICB': series('cicb_close', 'cicb_coupon_ex'),
     'BIZD': series('bizd_close', 'bizd_distribution_ex')}

def stats(s, start=None, end=None):
    s = [x for x in s if (start is None or x[0] >= start) and (end is None or x[0] <= end)]
    rets = [b[2] / a[2] - 1 for a, b in zip(s, s[1:])]
    m = sum(rets) / len(rets); vol = (sum((r - m) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5 * math.sqrt(252)
    peak = s[0][2]; pk_d = s[0][0]; mdd = 0; when = None
    for d, p, i in s:
        if i > peak:
            peak, pk_d = i, d
        dd = i / peak - 1
        if dd < mdd:
            mdd, when = dd, (pk_d, d)
    yrs = (len(s) - 1) / 252
    tr = s[-1][2] / s[0][2] - 1
    return dict(tr=tr, ann=(1 + tr) ** (1 / yrs) - 1, vol=vol, mdd=mdd, when=when, n=len(s))

print(f"from {R[0]['date']} to {R[-1]['date']}:")
ST = {}
for k, s in S.items():
    st = stats(s); ST[k] = st
    print(f"  {k}: total return {st['tr']:+.1%} ({st['ann']:+.1%} a year), volatility {st['vol']:.1%} a year, worst fall {st['mdd']:.1%} ({st['when'][0]} to {st['when'][1]})")
c, n = ST['CION common'], ST['CICB']
print(f"  CICB's worst fall was {n['mdd']/c['mdd']:.0%} of the common's; its volatility {n['vol']/c['vol']:.0%} of the common's")

# What CICB did while the common had its worst fall
a, b = c['when']
def idx_on(s, d):
    return [x for x in s if x[0] <= d][-1][2]
for k, s in S.items():
    print(f"  over the common's worst fall ({a} to {b}): {k} {idx_on(s, b)/idx_on(s, a)-1:+.1%}")

# The two cut announcements: close the day before to close the day after
for lab, d0, d1 in (("7 Jan 2026 cut, 36 to 30 cents", '2026-01-06', '2026-01-08'), ("5 Nov 2026 guide, 30 to 25 cents", '2026-11-04', '2026-11-06')):
    print(f"  {lab}: " + ", ".join(f"{k} {idx_on(s, d1)/idx_on(s, d0)-1:+.1%}" for k, s in S.items()))

# Calendar 2025, when CION's exits went worst
for k, s in S.items():
    st = stats(s, '2024-12-31', '2025-12-31')
    print(f"  2025: {k} total return {st['tr']:+.1%}, worst fall {st['mdd']:.1%}")
