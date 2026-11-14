# What the Pearl letter of intent would hand David's Bridal, against CION's marks.
from common import rows

T = {r['item']: r for r in rows('pearl_terms.csv')}
db_mark = 193042
for col, lab in (('zero_redemptions', 'no redemptions'), ('full_redemptions', 'full redemptions')):
    cash = float(T['cash_to_pearl_shareholders_musd'][col]); eq = float(T['equity_to_pearl_shareholders_musd'][col])
    for px in (10.0, 6.0, 3.0):
        v = cash + eq * px / 10
        print(f"  {lab:16s} Pearl at ${px:>4.1f}: cash {cash:.0f}m + stock {eq*px/10:.0f}m = {v:.0f}m to David's Bridal ({v*1000/db_mark:.0%} of CION's {db_mark/1000:.1f}m marks)")
rev = float(T['pearl_2026e_revenue_musd']['zero_redemptions']); m = float(T['pearl_2026e_ebitda_margin']['zero_redemptions'])
ev = float(T['pro_forma_enterprise_value_musd']['zero_redemptions'])
print(f"Pearl 2026E: revenue {rev:.0f}m, EBITDA ~{rev*m:.1f}m; EV {ev:.0f}m = {ev/(rev*m):.0f}x 2026E EBITDA, {ev/rev:.1f}x 2026E revenue")
print(f"K&F redemptions at the Nov 2026 extension vote: {float(T['kfii_shares_redeemed_nov_2026']['zero_redemptions']):,.0f} shares, ${T['kfii_redemption_amount_musd']['zero_redemptions']}m")
# Per share, against the stock price. My bear case (valuation.py) values David's Bridal at 40% of
# CION's marks, which is where I'd put it if the Pearl deal fails.
from common import inputs
I = inputs(); sh = I['shares_outstanding_2026_09_30'] / 1000; px = I['price_2026_11_13']
print(f"David's Bridal marks: ${db_mark/sh:.2f} a share, {db_mark/sh/px:.0%} of the ${px} price; at 40% of marks CION loses {db_mark*0.6:,.0f}k = ${db_mark*0.6/sh:.2f} a share")
