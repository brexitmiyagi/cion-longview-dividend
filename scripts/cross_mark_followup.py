# Does the cross-mark gap predict anything? If CION marking a loan above other lenders means its
# mark is stale, CION should mark those loans down later. I took every CION debt borrower that
# another listed BDC also held at 30 Sep 2024 and at 30 Sep 2025 (matched by company name from each
# lender's XBRL schedule of investments, data/cross_mark_followup.csv), and looked at where CION
# marked the same borrower 12 months later.
# Caveats: matching is by company, not tranche, so some pairs compare different loans (Isagenix
# and Avison Young look like that); a restructuring changes what CION holds under the same name;
# and positions CION exited drop out, because I can't see the exit price per loan.
import statistics as st
from common import rows

R = rows('cross_mark_followup.csv')
for cohort in sorted({r['cohort_date'] for r in R}) + ['both']:
    sel = [r for r in R if cohort in ('both', r['cohort_date'])]
    held = [r for r in sel if r['cion_mark_12m_later']]
    hi = [r for r in held if float(r['cion_mark_start']) - float(r['other_mark_avg']) > 0.10]
    lo = [r for r in held if float(r['cion_mark_start']) - float(r['other_mark_avg']) <= 0.10]
    ch = lambda rs: [100 * (float(r['cion_mark_12m_later']) - float(r['cion_mark_start'])) for r in rs]
    gaps = [100 * (float(r['cion_mark_start']) - float(r['other_mark_avg'])) for r in held]
    x = ch(held)
    mx, my = st.mean(gaps), st.mean(x)
    corr = sum((a - mx) * (b - my) for a, b in zip(gaps, x)) / ((sum((a - mx) ** 2 for a in gaps) * sum((b - my) ** 2 for b in x)) ** 0.5)
    print(f"{cohort}: {len(sel)} shared borrowers, {len(sel)-len(held)} exited, {len(held)} still held a year later")
    print(f"  CION more than 10 points above the others ({len(hi)}): next-12-month change in CION's mark, mean {st.mean(ch(hi)):+.1f} pts, median {st.median(ch(hi)):+.1f}")
    print(f"  the rest ({len(lo)}): mean {st.mean(ch(lo)):+.1f} pts, median {st.median(ch(lo)):+.1f}")
    print(f"  correlation of the gap with the later change: {corr:+.2f}")
