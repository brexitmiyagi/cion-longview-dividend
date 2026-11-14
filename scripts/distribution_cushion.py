# How much is there to pay the distribution from, beyond what CION earns each quarter?
# A BDC can carry undistributed taxable income ("spillover") into the next year and pay from it.
from common import inputs

I = inputs()
sh = I['shares_outstanding_2026_09_30'] / 1000
u = I['undistributed_ordinary_income_2025_12_31']
print(f"undistributed ordinary income on a tax basis, 31 Dec 2025: {u:,.0f}k = ${u/sh:.3f}/share, {u/(0.25*sh):.2f} quarters of a 25 cent distribution")
over = I['distributions_9m_2026'] - I['nii_9m_2026']
print(f"first nine months of 2026: distributions {I['distributions_9m_2026']:,.0f}k vs NII {I['nii_9m_2026']:,.0f}k, paid out {over:,.0f}k more than earned (${over/sh:.2f}/share; book basis, tax basis is set at year end)")
for nii in (0.17, 0.19, 0.21):
    gap = 0.25 - nii
    print(f"  NII ${nii:.2f} against $0.25: short ${gap:.2f} a quarter, ${gap*sh:,.0f}k; a year of that is ${gap*4:.2f}/share")
lv_gain = 99241 - 12917
cf = I['capital_loss_carryforward_2025_12_31']
print(f"Longview sold at the 30 Sep mark would realize about {lv_gain:,.0f}k over cost; capital loss carryforwards were {cf:,.0f}k at 31 Dec 2025, before 2026's realized losses")
