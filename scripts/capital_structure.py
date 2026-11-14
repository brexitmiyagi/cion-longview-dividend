# Asset coverage at book and at the share price, and what the listed notes yield.
from datetime import date
from common import inputs, rows, note_yield

I = inputs()
sh = I['shares_outstanding_2026_09_30'] / 1000
debt, na = I['debt_principal'], I['net_assets_2026_09_30']
mcap = I['price_2026_11_13'] * sh
print(f"asset coverage at book: ({na:,.0f} + {debt:,.0f}) / {debt:,.0f} = {(na+debt)/debt:.0%} (10-Q: 172%)")
print(f"NAV could fall {na - (I['asset_coverage_min']-1)*debt:,.0f}k ({1-(I['asset_coverage_min']-1)*debt/na:.0%}) before coverage hits 150%")
print(f"asset coverage if NAV were the market cap ({mcap:,.0f}k): {(mcap+debt)/debt:.0%}")

for r in rows('bonds.csv'):
    y, m, d = map(int, r['maturity'].split('-'))
    print(f"{r['ticker']}: ${r['price_2026_11_13']} for ${r['par']} par, {float(r['coupon']):.1%} coupon, due {r['maturity']}: yield to maturity ~{note_yield(float(r['price_2026_11_13']), float(r['coupon']), date(y,m,d), date(2026, 11, 13)):.2%}")
