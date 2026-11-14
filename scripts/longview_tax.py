# Does selling Longview force a special distribution? CION is a RIC and must pay out its taxable
# income. A gain on Longview is a capital gain, and CION has long-term capital loss carryforwards
# from earlier years (10-Q Q3 2026, Note 5). If the carryforwards cover the gain, CION can keep the
# cash for buybacks and debt.
from common import inputs
I = inputs()
cost = 12917            # Longview cost, 30 Sep 2026 schedule (longview_dividend.py); tax cost may differ
cf = 66847              # long-term capital loss carryforwards, 31 Dec 2025 (10-Q Q3 2026, Note 5)
for lab, share in (('bear, 41% of mark', 0.41), ('base, 80% of mark', 0.80), ('full mark', 1.00), ('154% of mark', 1.54)):
    p = 99241 * share; g = p - cost
    print(f"  {lab}: proceeds {p:,.0f}k, gain on book cost {g:,.0f}k, against {cf:,.0f}k of carryforwards: {'covered' if g <= cf else f'{g-cf:,.0f}k not covered'}")
print("  caveat: tax cost and book cost can differ, and other 2026-27 gains or losses also use the carryforwards")
