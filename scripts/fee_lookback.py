# Most BDC advisers, like CION's, keep income fees earned on PIK that's later written off
# (data/peer_advisory_terms.csv). Two of the six peers I checked, Blackstone Secured Lending and
# Oaktree Specialty Lending, cap the income fee instead: 17.5% of pre-incentive NII minus net capital
# losses over the trailing twelve quarters, less fees already paid in the previous eleven. Losses on
# PIK loans then cut the fee. What would that cap have done at CION?
# Data back to Q1 2023 lets me apply it from Q4 2025, quarter by quarter, with the capped fees fed
# into later quarters.
from common import inputs, rows, incentive_fee

I = inputs()
H = rows('fee_history_quarterly.csv')
NA = {r['quarter_end']: float(r['net_assets_start_k']) for r in rows('income_and_fees_quarterly.csv')}
pre = [float(r['nii_before_tax_k']) + float(r['incentive_fee_k']) for r in H]
gl = [float(r['net_realized_unrealized_k']) for r in H]
paid = [float(r['incentive_fee_k']) for r in H]
qs = [r['quarter_end'] for r in H]
start = qs.index('2025-12-31')
actual = capped = 0.0
for i in range(start, len(qs)):
    w = range(i - 11, i + 1)
    net_loss = -min(0.0, sum(gl[j] for j in w))
    cum = sum(pre[j] for j in w) - net_loss
    cap = 0.175 * cum - sum(paid[j] for j in range(i - 11, i))
    fee = float(H[i]['incentive_fee_k'])
    new = max(0.0, min(fee, cap))
    paid[i] = new
    actual += fee; capped += new
    print(f"  {qs[i]}: trailing 12 quarters pre-incentive NII {sum(pre[j] for j in w):,.0f}k, net capital loss {net_loss:,.0f}k -> cap {cap:,.0f}k; fee paid {fee:,.0f}k, under the cap {new:,.0f}k")
print(f"Q4 2025 to Q3 2026: CION paid {actual:,.0f}k; with a Blackstone/Oaktree-style lookback it would have paid {capped:,.0f}k")
sh = I['shares_outstanding_2026_09_30'] / 1000
print(f"  per share: {actual/sh*100:.1f} cents of NII over four quarters, against a 25 cent quarterly distribution from 2027")
