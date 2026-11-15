# CION next to every externally managed BDC in my 18-BDC peer panel (data/peer_bdcs_2026_09.csv)
# with a market cap under $1 billion and a price under 0.75x NAV, all on 30 Sep 2026 numbers.
# The rule picks the peers; the script applies it. Coverage is nine-month NII over nine-month distributions. PIK share is nine-month PIK
# income over nine-month total investment income. Non-accruals are at fair value, as each 10-Q
# reports them (PSBD says "less than 0.01%"; HRZN gives $18.8 million, which I divide by its
# $650.3 million of investments at fair value). Asset coverage is from each 10-Q; debt to equity is
# roughly 1 / (asset coverage - 1). Prices are 13 Nov 2026 closes.
import os, csv
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'data')
P = {r['ticker']: r for r in csv.DictReader(open(os.path.join(D, 'peer_bdcs_2026_09.csv')))}
C = {r['ticker']: r for r in csv.DictReader(open(os.path.join(D, 'peer_credit_2026_09_30.csv')))}
EXTERNAL = {'ARCC', 'BBDC', 'BCSF', 'BXSL', 'CGBD', 'FSK', 'HRZN', 'MFIC', 'MSDL', 'NCDL', 'OBDC', 'OFS', 'OTF', 'PSBD', 'RAND', 'TCPC', 'TSLX', 'CION'}  # HTGC is internally managed
def mcap(p): return float(p['price_2026_11_13']) * float(p['shares_2026_09_30'])
def pn(p): return float(p['price_2026_11_13']) / float(p['nav_per_share_2026_09_30'])
picked = sorted([t for t, p in P.items() if t != 'CION' and t in EXTERNAL and mcap(p) < 1e9 and pn(p) < 0.75], key=lambda t: pn(P[t]))
print('peers by the rule:', ', '.join(f"{t} (${mcap(P[t])/1e6:,.0f}m, {pn(P[t]):.2f}x)" for t in picked))
print('ticker | price/NAV | NII/distributions (9m) | PIK % of income (9m) | non-accruals at FV | asset coverage | debt/equity (approx.)')
for t in ['CION'] + picked:
    p, c = P[t], C[t]
    pnav = float(p['price_2026_11_13']) / float(p['nav_per_share_2026_09_30'])
    cov = float(p['nii_9m']) / float(p['distributions_9m'])
    pik = float(p['pik_9m']) / float(p['total_investment_income_9m'])
    ac = float(c['asset_coverage_pct']) / 100
    na = float(c['nonaccrual_fair_value_pct'])
    nas = '<0.01%' if na <= 0.01 else f'{na:.1f}%'
    print(f'{t} | {pnav:.2f}x | {cov:.2f}x | {pik:.1%} | {nas} | {ac:.0%} | {1/(ac-1):.2f}x')
cion = P['CION']
print(f"CION nine-month PIK income {float(cion['pik_9m'])/1e3:,.0f}k against NII {float(cion['nii_9m'])/1e3:,.0f}k: {float(cion['pik_9m'])/float(cion['nii_9m']):.0%} of NII, {float(cion['pik_9m'])/float(cion['total_investment_income_9m']):.1%} of total investment income")
