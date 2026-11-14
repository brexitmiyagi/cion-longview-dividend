# What happens to a BDC's price when it cuts its regular distribution? Every regular cut of 10% or
# more I could match to the press release that announced it, 2024 to 2026 (data/bdc_dividend_cuts.csv:
# ex-dates from Yahoo, announcement and new amount checked in each 8-K's exhibit 99.1; CION's 2027
# cut is from its Q3 2026 results and call). The move is the close before the announcement to the
# close the trading day after, against BIZD, the BDC ETF, over the same days. It includes whatever
# else was in the results, so it's the reaction to the whole release, not the cut alone.
import statistics as st
from common import rows

R = rows('bdc_dividend_cuts.csv')
out = []
for r in R:
    o, n, f = float(r['old_regular']), float(r['new_regular']), int(r['payments_per_year'])
    p0, p1 = float(r['close_before']), float(r['close_after'])
    b0, b1 = float(r['bizd_before']), float(r['bizd_after'])
    rel = (p1 / p0) / (b1 / b0) - 1
    y = o * f / p0
    out.append((r['ticker'], r['announced'], 1 - n / o, y, p1 / p0 - 1, rel))
    print(f"  {r['ticker']:5s} {r['announced']}: cut {1-n/o:.0%}, yield before {y:.1%}, stock {p1/p0-1:+.1%}, against BIZD {rel:+.1%}")
rel = [x[5] for x in out]
print(f"{len(out)} cuts: median move against BIZD {st.median(rel):+.1%}; fell more than BIZD in {sum(1 for x in rel if x < 0)} of {len(rel)}")
hi = [x[5] for x in out if x[3] >= 0.13]; lo = [x[5] for x in out if x[3] < 0.13]
print(f"  yield of 13% or more before the cut ({len(hi)}): median {st.median(hi):+.1%}; under 13% ({len(lo)}): median {st.median(lo):+.1%}")
c = [x for x in out if x[0] == 'CION']
print("CION's own: " + "; ".join(f"{d} cut {k:.0%}, {r_:+.1%} against BIZD" for _, d, k, _, _, r_ in c))
