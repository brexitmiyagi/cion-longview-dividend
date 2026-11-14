# Do CION's valuation assumptions explain why its marks run high? The 10-Q's Level 3 inputs table
# gives the discount rates used on loans valued by discounted cash flow. Higher rates mean lower
# values. CION's are higher than FS KKR's and OFS's, not lower, so the headline inputs don't
# explain it. What the table doesn't show is the cash flows those rates are applied to,
# including whether PIK is assumed to be collected in full.
from common import rows
for r in rows('level3_inputs_2026_09_30.csv'):
    y = f", yield on debt {r['yield_on_debt']}% ({r['yield_basis']})" if r['yield_on_debt'] else ''
    gap = f"; discount rate minus yield {float(r['discount_rate_weighted'])-float(r['yield_on_debt']):.1f} points" if r['yield_on_debt'] else ''
    print(f"  {r['lender']:18s} {r['asset']}: {float(r['fair_value']):,.0f} ({r['units']}) by DCF, discount rates {r['discount_rate_low']}% to {r['discount_rate_high']}%, weighted {r['discount_rate_weighted']}%{y}{gap}")
