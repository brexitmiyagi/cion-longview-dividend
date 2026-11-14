# Checks the numbers I took from the 10-Q add up the way the 10-Q says they do.
# Fails loudly if any of them don't.
from common import inputs, rows, incentive_fee

I = inputs()
lv = {r['period_end']: r for r in rows('longview.csv')}
q3_lv = float(lv['2026-09-30']['dividend_income_ytd_k']) - float(lv['2026-06-30']['dividend_income_ytd_k'])
assert q3_lv <= I['q3_affiliated_dividend_income'], 'Longview Q3 dividend bigger than all affiliated dividends'
fee = incentive_fee(I['q3_nii_after_tax'] + I['q3_incentive_fee'], I['net_assets_2026_06_30'], I)
assert abs(fee - I['q3_incentive_fee']) < 10, f'incentive fee does not tie: {fee}'
debt = sum(float(r['amount_k']) for r in rows('debt_2026_09_30.csv'))
assert debt == I['debt_principal'], f'debt table {debt} vs {I["debt_principal"]}'
nav = I['net_assets_2026_09_30'] / (I['shares_outstanding_2026_09_30'] / 1000)
assert abs(nav - I['nav_per_share_2026_09_30']) < 0.005, f'NAV per share {nav}'
slfp = sum(float(r['fair_value_k']) for r in rows('slfp_loans_2026_09_30.csv'))
assert abs(slfp - 176909) < 1, f'SLFP loans {slfp}'
dist = 0.30 * I['shares_outstanding_2026_09_30'] / 1000
assert abs(dist - I['q3_distributions_paid']) < 100, f'distributions {dist}'
print('tie-out OK: Longview Q3 dividend', q3_lv, '| incentive fee', round(fee), '| debt', debt, '| NAV/share', round(nav, 2), '| SLFP loans', slfp, '| distributions', round(dist))
import book_quality as bq
assert abs(sum(v[1] for v in bq.B.values()) - I['investments_fv_ex_short_term']) < 1, 'schedule buckets do not sum to the portfolio'
lu = rows('longview_units.csv')[-1]
assert float(lu['fair_value_k']) == float(lv['2026-09-30']['fair_value_k']), 'Longview mark mismatch between files'
print('tie-out OK: schedule buckets sum to', round(sum(v[1] for v in bq.B.values())), '| Longview mark consistent')

# the PIK bucket total pik_cross_marks.py uses must match book_quality.py
import pik_cross_marks as pcm
assert abs(bq.B['Debt with PIK'][1] - pcm.PIK_BUCKET) < 1, f"PIK bucket {bq.B['Debt with PIK'][1]} vs {pcm.PIK_BUCKET}"
# every CION fair value in the cross-mark file must be a line in the 30 Sep schedule
fvs = {float(r['fair_value_k']) for r in rows('schedule_2026_09_30.csv')}
for r in rows('pik_cross_marks.csv'):
    assert float(r['cion_fair_value_k']) in fvs, f"{r['company']} {r['cion_fair_value_k']} not in schedule"
print('PIK cross-marks tie to the schedule')

# the Level 3 rollforward quarters for 2026 add up to the nine-month realized loss in the 10-Q
L3 = {r['quarter']: r for r in rows('level3_rollforward.csv')}
r26 = sum(float(L3[q]['net_realized_k']) for q in ('Q1 2026', 'Q2 2026', 'Q3 2026'))
assert abs(r26 - (-26360)) < 2, f'Level 3 realized 2026 {r26}'
# the quarterly credit-loss file adds up to the nine-month figure on the statement of operations
CL = {r['quarter']: float(r['net_realized_and_unrealized_k']) for r in rows('credit_losses_by_quarter.csv')}
assert abs(CL['Q1 2026'] + CL['Q2 2026'] + CL['Q3 2026'] - (-34962)) < 2, 'credit losses 2026 do not add up'
assert abs(CL['Q1 2025'] + CL['Q2 2025'] + CL['Q3 2025'] + CL['Q4 2025'] - CL['FY 2025']) < 2, 'credit losses 2025 do not add up'
print('Level 3 rollforward and quarterly credit losses tie to the statements')

# the incentive fee formula rebuilds every quarter's reported fee
for r in rows('income_and_fees_quarterly.csv'):
    pre = float(r['nii_before_tax_k']) + float(r['incentive_fee_k'])
    assert abs(incentive_fee(pre, float(r['net_assets_start_k']), I) - float(r['incentive_fee_k'])) < 30, f"fee does not rebuild for {r['quarter_end']}"
print('incentive fee rebuilds within $30k in every quarter, Q1 2024 to Q3 2026')
