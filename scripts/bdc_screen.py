# Sector screen. How much of what BDCs pay out is covered by net investment income,
# and how much is covered once PIK income (interest paid in more debt) is taken out.
# Input is data/bdc_panel.csv, built from SEC XBRL company facts by pull_bdc_panel.py.
import os, csv, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

# not BDCs, they just use the same XBRL tags (checked against their SEC filer records)
NOT_BDC = {'1684682': 'CNL Strategic Capital (operating LLC)', '1971381': 'Apollo Infrastructure Co (infrastructure LLC)'}


def num(x):
    return float(x) if x not in ('', None) else None


rows = []
for r in csv.DictReader(open(os.path.join(DATA, 'bdc_panel.csv'))):
    for k in ('nii', 'total_investment_income', 'pik_income', 'distributions_declared',
              'drip_shares_issued', 'undistributed_ordinary_income_yearend'):
        r[k] = num(r[k])
    rows.append(r)

excluded = []


def usable(r):
    if r['cik'] in NOT_BDC:
        return False
    if r['pik_income'] is None or not r['nii'] or not r['distributions_declared']:
        return False
    if r['nii'] <= 0 or r['distributions_declared'] <= 0:
        return False
    # a BDC has to pay out about 90% of taxable income, so NII at half or 2.5x of
    # distributions for a full period is almost always a tagging error (a quarter
    # tagged as a year, say). I drop those and print them.
    c = r['nii'] / r['distributions_declared']
    if c < 0.5 or c > 2.5:
        excluded.append(r)
        return False
    return True


M = {(r['cik'], r['period_kind'], r['period']): r for r in rows if usable(r)}


def agg(R):
    nii = sum(r['nii'] for r in R); pik = sum(r['pik_income'] for r in R); dv = sum(r['distributions_declared'] for r in R)
    return nii, pik, dv


def constant_panel(kind, periods, listed=None):
    ciks = {c for (c, k, p) in M if k == kind}
    keep = [c for c in ciks if all((c, kind, p) in M for p in periods)]
    if listed is not None:
        keep = [c for c in keep if bool(M[(c, kind, periods[-1])]['ticker']) == listed]
    return sorted(keep)


print('rows dropped as likely tagging errors:')
for r in excluded:
    print(f"  {r['name'][:45]:45s} {r['period_kind']} {r['period']}: NII {r['nii']/1e6:,.1f}m vs distributions {r['distributions_declared']/1e6:,.1f}m")
print()

for label, listed in (('all', None), ('listed', True), ('non-traded', False)):
    P = ['2022', '2023', '2024', '2025']
    keep = constant_panel('FY', P, listed)
    print(f"full years, constant panel of {len(keep)} BDCs ({label}) that filed all of {P[0]}-{P[-1]}")
    for p in P:
        R = [M[(c, 'FY', p)] for c in keep]
        nii, pik, dv = agg(R)
        short = sum(1 for r in R if r['nii'] < r['distributions_declared'])
        short_x = sum(1 for r in R if r['nii'] - r['pik_income'] < r['distributions_declared'])
        print(f"  {p}: NII ${nii/1e9:.2f}bn, PIK ${pik/1e9:.2f}bn ({pik/nii:.0%} of NII), distributions ${dv/1e9:.2f}bn;"
              f" NII covers {nii/dv:.2f}x, NII ex-PIK covers {(nii-pik)/dv:.2f}x;"
              f" short on NII {short}, short ex-PIK {short_x}")
    print()

# how NII and distributions grew 2023 to 2025 at each BDC in the full panel
keep = constant_panel('FY', ['2022', '2023', '2024', '2025'])
g_n = [M[(c, 'FY', '2025')]['nii'] / M[(c, 'FY', '2023')]['nii'] - 1 for c in keep]
g_d = [M[(c, 'FY', '2025')]['distributions_declared'] / M[(c, 'FY', '2023')]['distributions_declared'] - 1 for c in keep]
fell = sum(1 for c in keep if M[(c, 'FY', '2025')]['nii'] / M[(c, 'FY', '2025')]['distributions_declared']
           < M[(c, 'FY', '2023')]['nii'] / M[(c, 'FY', '2023')]['distributions_declared'])
print(f"2023 to 2025, median BDC in that panel: NII {st.median(g_n):+.0%}, distributions {st.median(g_d):+.0%}; coverage fell at {fell} of {len(keep)}")
print()

# who reinvests the distribution, and how much undistributed income is left to lean on
for p in ('2023', '2024', '2025'):
    for listed in (True, False):
        R = [r for (c, k, pp), r in M.items() if k == 'FY' and pp == p and bool(r['ticker']) == listed]
        D = [r for r in R if r['drip_shares_issued'] is not None]
        S = [r for r in R if r['undistributed_ordinary_income_yearend'] is not None]
        drip = sum(r['drip_shares_issued'] for r in D) / sum(r['distributions_declared'] for r in D)
        cash_out = sum(r['distributions_declared'] - r['drip_shares_issued'] for r in D)
        expik = sum(r['nii'] - r['pik_income'] for r in D)
        months = st.median(r['undistributed_ordinary_income_yearend'] / r['distributions_declared'] * 12 for r in S)
        print(f"{p} {'listed' if listed else 'non-traded'}: {len(R)} BDCs; {drip:.0%} of distributions went back out as new shares"
              f" (n={len(D)}), NII ex-PIK covers the cash part {expik/cash_out:.2f}x; median undistributed income"
              f" at year end = {months:.1f} months of distributions (n={len(S)})")
print()

# first nine months of 2026, every BDC that has filed both 9M periods
L = []
for (c, k, p), r in M.items():
    if k == '9M' and p == '2026-09' and (c, '9M', '2025-09') in M:
        a = M[(c, '9M', '2025-09')]
        L.append((r, (r['nii'] - r['pik_income']) / r['distributions_declared'], r['distributions_declared'] / a['distributions_declared'] - 1))
L.sort(key=lambda x: x[1])
R = [x[0] for x in L]
nii, pik, dv = agg(R)
print(f"nine months to September 2026, {len(L)} BDCs: NII covers {nii/dv:.2f}x, ex-PIK {(nii-pik)/dv:.2f}x, PIK {pik/nii:.0%} of NII")
for r, x, g in L:
    print(f"  {r['name'][:40]:40s} {r['ticker'] or 'non-traded':10s} NII {r['nii']/1e6:8.1f}m  PIK {r['pik_income']/1e6:7.1f}m"
          f"  paid {r['distributions_declared']/1e6:7.1f}m  NII cover {r['nii']/r['distributions_declared']:.2f}  ex-PIK {x:.2f}"
          f"  distributions vs 9M 2025 {g:+.0%}")
