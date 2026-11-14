# How much of the adviser's income incentive fee depends on PIK income?
# CION's fee: nothing until pre-incentive NII reaches 1.625% of net assets at the start of the
# quarter, then 100% of the excess up to 1.970%, then 17.5%. Pre-incentive NII includes accrued
# PIK. The 10-K says CIM doesn't have to pay any of it back if that PIK is never collected.
# For each quarter: rebuild the fee from the filings, then rerun it with the PIK income taken out.
from common import inputs, rows, incentive_fee

I = inputs()
R = rows('income_and_fees_quarterly.csv')
tot_fee = tot_pik_part = tot_pik = 0.0
print("quarter     | PIK income | fee reported | fee rebuilt | fee without PIK | fee that depends on PIK")
for r in R:
    pre = float(r['nii_before_tax_k']) + float(r['incentive_fee_k'])
    na = float(r['net_assets_start_k'])
    rebuilt = incentive_fee(pre, na, I)
    without = incentive_fee(pre - float(r['pik_income_k']), na, I)
    part = rebuilt - without
    tot_fee += float(r['incentive_fee_k']); tot_pik_part += part; tot_pik += float(r['pik_income_k'])
    print(f"  {r['quarter_end']}  {float(r['pik_income_k']):9,.0f}k  {float(r['incentive_fee_k']):9,.0f}k  {rebuilt:9,.0f}k  {without:9,.0f}k  {part:9,.0f}k ({part/rebuilt:.0%})")
print(f"Q1 2024 to Q3 2026: incentive fees {tot_fee:,.0f}k, of which {tot_pik_part:,.0f}k ({tot_pik_part/tot_fee:.0%}) would not have been earned without PIK income;")
print(f"  PIK income booked over the same period {tot_pik:,.0f}k")
since = [r for r in R if r['quarter_end'] >= '2024-12-31']
zero = [r['quarter_end'] for r in since if incentive_fee(float(r['nii_before_tax_k']) + float(r['incentive_fee_k']) - float(r['pik_income_k']), float(r['net_assets_start_k']), I) == 0]
print(f"quarters since Q4 2024 where the whole fee depends on PIK: {len(zero)} of {len(since)}")
print("the advisory agreement, per the 2025 10-K: CIM is not under any obligation to reimburse the Company for any part")
print("  of the subordinated incentive fee on income CIM received that was based on accrued income that the Company never actually received")

# The fairer counterfactual: not all PIK is lost. valuation.py's base case expects 79% of the PIK
# loans' value to be recovered, so take out only the other 21% of PIK income and see how much fee
# was paid on it.
RECOVERY = 0.79
lost_fee = 0.0
for r in R:
    pre = float(r['nii_before_tax_k']) + float(r['incentive_fee_k'])
    na = float(r['net_assets_start_k'])
    lost_fee += incentive_fee(pre, na, I) - incentive_fee(pre - float(r['pik_income_k']) * (1 - RECOVERY), na, I)
print(f"at {RECOVERY:.0%} recovery, fees paid on the {1-RECOVERY:.0%} of PIK income I don't expect to be collected: {lost_fee:,.0f}k"
      f" ({lost_fee/tot_fee:.0%} of all income fees, Q1 2024 to Q3 2026)")
# The 79% is my base case, not a fact. The same number at 70% and 90%:
for rec in (0.70, 0.90):
    lf = 0.0
    for r in R:
        pre = float(r['nii_before_tax_k']) + float(r['incentive_fee_k'])
        na = float(r['net_assets_start_k'])
        lf += incentive_fee(pre, na, I) - incentive_fee(pre - float(r['pik_income_k']) * (1 - rec), na, I)
    print(f"  at {rec:.0%} recovery: {lf:,.0f}k ({lf/tot_fee:.0%} of income fees)")
# Scale. Over eleven quarters, per year, per share (shares at 30 Sep 2026) and against NII.
yrs = len(R) / 4
sh_now = I['shares_outstanding_2026_09_30'] / 1000
nii_tot = sum(float(r['nii_before_tax_k']) for r in R)
print(f"scale at 79%: {lost_fee/yrs:,.0f}k a year, {lost_fee/yrs/sh_now*100:.1f} cents a share a year, {lost_fee/nii_tot:.1%} of NII over the period ({nii_tot:,.0f}k)")
