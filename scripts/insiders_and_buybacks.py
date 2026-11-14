# Two quick checks on what management does with its own money and CION's.
# Insiders: every Form 4 filed under CION's CIK since 2024 (data/cion_form4_2024_2026.csv, parsed from
# the XML on EDGAR). Buybacks: shares repurchased and cash paid, year to date, from XBRL
# (data/cion_buybacks_ytd.csv).
from common import rows, inputs
I = inputs()
F = rows('cion_form4_2024_2026.csv')
buys = [r for r in F if r['code'] == 'P']
tot = sum(float(r['shares']) * float(r['price']) for r in buys)
print(f"open-market purchases by officers and directors, Jan 2024 to 14 Nov 2026: {len(buys)} trades, about ${tot:,.0f}, average ${tot/sum(float(r['shares']) for r in buys):.2f} a share")
print(f"  sales: {sum(1 for r in F if r['code'] == 'S')}; last purchase {buys[-1]['transaction_date']} ({buys[-1]['owner'].title()}) at ${float(buys[-1]['price']):.2f}")
print(f"  none filed since then; the stock is ${I['price_2026_11_13']} now, {I['price_2026_11_13']/float(buys[-1]['price'])-1:+.0%} from that last purchase, at {I['price_2026_11_13']/I['nav_per_share_2026_09_30']:.2f}x NAV")
B = rows('cion_buybacks_ytd.csv')
yr = {r['period_end_ytd'][:4]: r for r in B if r['period_end_ytd'][5:] == '12-31'}
for y in ('2023', '2024', '2025'):
    r = yr[y]; print(f"buybacks {y}: {float(r['shares_repurchased']):,.0f} shares for ${float(r['usd_paid'])/1e6:.1f}m (avg ${float(r['usd_paid'])/float(r['shares_repurchased']):.2f})")
q = {r['period_end_ytd']: r for r in B}
h1 = q['2026-06-30']; q3 = q['2026-09-30']
print(f"buybacks 2026: first half {float(h1['shares_repurchased']):,.0f} shares for ${float(h1['usd_paid'])/1e6:.1f}m (avg ${float(h1['usd_paid'])/float(h1['shares_repurchased']):.2f}); Q3 none")
print(f"remaining authorization {I['buyback_authorization_remaining']/1000:.1f}m; my base case spends about $55m of it in Q2-Q3 2027, about three times the pace of the busiest half-year above")
