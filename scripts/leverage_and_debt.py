# What the deleveraging did, and what is left to refinance.
from common import inputs, rows

I = inputs()
sofr = I['sofr_3m_2026_09_30']
na = I['net_assets_2026_09_30']
cash = I['cash'] + I['short_term_investments']
debt = I['debt_principal']
print(f"reported net debt/equity: ({debt:,.0f} - {cash:,.0f}) / {na:,.0f} = {(debt-cash)/na:.2f}x")
# Look-through: CION owns all of SLFP's common equity, which sits under $125m of notes
# and $11.9m of preferred. The notes are non-recourse to CION, so this is economic, not legal.
lt = (debt - cash + I['slfp_notes'] + I['slfp_pref_liquidation']) / na
print(f"look-through net debt/equity incl. SLFP notes and preferred: {lt:.2f}x (30 June reported: 1.52x)")
print(f"SLFP: {I['slfp_loans_sold_par']:,.0f}k par sold for {I['slfp_loans_sold_price']:,.0f}k = {I['slfp_loans_sold_price']/I['slfp_loans_sold_par']:.1%} of par")
nc = I['slfp_sale_paid_in_jv_equity']
print(f"  of which {nc:,.0f}k was paid in SLFP common equity, not cash (10-Q cash flow statement), so cash in was {I['slfp_loans_sold_price']-nc:,.0f}k ({(I['slfp_loans_sold_price']-nc)/I['slfp_loans_sold_price']:.0%})")

def all_in(r):
    s = float(r.get('spread_or_coupon') or r.get('spread'))
    return sofr + s if r['floating'] == '1' else s

print('\nDebt repaid in Q3 (all-in at 30 Sep SOFR of 4.11%):')
for r in rows('debt_repaid_q3_2026.csv'):
    print(f"  {r['facility']:30s} {float(r['amount_k']):>9,.0f}k  {all_in(r):.2%}  repaid {r['repaid']}  ({r['note']})")
print(f"  SLFP notes (new, off balance sheet)    {I['slfp_notes']:>9,.0f}k  {sofr+0.0475:.2%}")
print('\nDebt outstanding 30 Sep 2026, cheapest first:')
D = sorted(rows('debt_2026_09_30.csv'), key=all_in)
tot = sum(float(r['amount_k']) for r in D)
wavg = sum(float(r['amount_k']) * all_in(r) for r in D) / tot
for r in D:
    print(f"  {r['facility']:36s} {float(r['amount_k']):>9,.0f}k  {all_in(r):.2%}  due {r['maturity']}")
print(f"  total {tot:,.0f}k, weighted all-in {wavg:.2%} (company reports 7.6% for the quarter)")
due27 = sum(float(r['amount_k']) for r in D if r['maturity'].startswith('2027'))
print(f"due in 2027: {due27:,.0f}k = {due27/tot:.0%} of debt; cash and short-term investments {cash:,.0f}k; undrawn {25000:,.0f}k")
print(f"yield on total investments at cost 8.27% vs weighted debt cost {wavg:.2%}: spread {0.0827-wavg:.2%}")
