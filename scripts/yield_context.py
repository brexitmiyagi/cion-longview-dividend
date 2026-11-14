# Is a cut already in the price? CION's yield on the 2027 base distribution against what listed
# peers pay. Peers: trailing yield on distributions declared in the first nine months of 2026,
# annualised, over the 13 Nov 2026 close (data/peer_bdcs_2026_09.csv). That includes specials,
# so it flatters some peers; it's a rough comparison, not a forecast of anyone's payout.
import statistics as st
from common import inputs, rows

I = inputs()
px = I['price_2026_11_13']
cion = 0.25 * 4 / px
ys = []
for r in rows('peer_bdcs_2026_09.csv'):
    if r['ticker'] == 'CION': continue
    y = float(r['distributions_9m']) / float(r['shares_2026_09_30']) * 4 / 3 / float(r['price_2026_11_13'])
    ys.append((r['ticker'], y))
ys.sort(key=lambda x: -x[1])
print(f"CION at $0.25 a quarter on ${px}: {cion:.1%}")
print("peers, trailing nine months annualised: " + ", ".join(f"{t} {y:.1%}" for t, y in ys))
print(f"peer median {st.median(y for _, y in ys):.1%}; CION ranks {sum(1 for _, y in ys if y > cion) + 1} of {len(ys) + 1}")
for cut in (0.21, 0.20):
    print(f"  if CION paid ${cut:.2f} a quarter, the yield at today's price would be {cut*4/px:.1%}")
