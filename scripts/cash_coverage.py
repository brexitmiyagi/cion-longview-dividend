# How much of CION's distribution was earned in something other than more loan paper.
# Main measure: NII minus PIK income, against distributions declared. It's the same measure
# bdc_screen.py runs across the sector, so CION can be compared with everyone else.
# The wider cash basis (also taking out discount accretion and adding back debt-cost
# amortization) is printed underneath. I don't lean on it, because both of those reflect
# cash that moved earlier, so they're arguable either way.
from common import rows

for r in rows('cash_basis.csv'):
    nii, pik = float(r['nii_k']), float(r['pik_capitalized_k'])
    acc, am = (float(r[k] or 0) for k in ('discount_accretion_k', 'debt_cost_amortization_k'))
    dec = float(r['distributions_declared_k'])
    x = nii - pik
    line = (f"{r['period']}: NII {nii:,.0f}k, PIK {pik:,.0f}k ({pik/nii:.0%} of NII); NII ex-PIK {x:,.0f}k vs distributions declared"
            f" {dec:,.0f}k = {x/dec:.2f}x")
    if r['longview_dividends_k']:
        lv = float(r['longview_dividends_k'])
        line += f"; without Longview's {lv:,.0f}k: {x-lv:,.0f}k"
    print(line)
    if not r["discount_accretion_k"]:
        continue
    wide = nii - pik - acc + am
    print(f"    wider cash basis (also minus accretion, plus debt-cost amortization): {wide:,.0f}k = {wide/dec:.2f}x")
