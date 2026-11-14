# Cross-mark CION's loans against other lenders who hold the same loans.
# Method: the same one I used on Longview. Search EDGAR full text for each of CION's largest
# PIK names in 30 Sep 2026 filings, keep the hits that are other funds' schedules of
# investments, and compare marks as a percent of par on the same tranche where I could
# match it. Where two other lenders hold it, I use the average of their marks.
# What this can't do: most of CION's biggest PIK loans have no other public holder.
from collections import defaultdict
from common import inputs, rows

I = inputs()
sh = I['shares_outstanding_2026_09_30'] / 1000
X = rows('pik_cross_marks.csv')

by = defaultdict(list)
for r in X:
    by[(r['company'], r['tranche'])].append(r)

tot_fv = tot_avg = tot_low = 0.0
pik_fv = pik_avg = 0.0
print("loan | CION mark | other lenders | CION's mark at their average")
for (co, tr), rs in by.items():
    fv = float(rs[0]['cion_fair_value_k']); mine = float(rs[0]['cion_mark_pct_par'])
    others = [float(r['other_mark_pct_par']) for r in rs]
    avg = sum(others) / len(others); low = min(others)
    at_avg = fv * avg / mine; at_low = fv * low / mine
    tot_fv += fv; tot_avg += at_avg; tot_low += at_low
    if rs[0]['in_cion_pik_bucket'] == 'yes':
        pik_fv += fv; pik_avg += at_avg
    names = '; '.join(f"{r['other_holder']} {float(r['other_mark_pct_par']):.1f}%" for r in rs)
    print(f"  {co}, {tr}: {mine:.1f}% ({fv:,.0f}k) | {names} | {at_avg:,.0f}k ({at_avg-fv:+,.0f}k)")
print()
print(f"shared loans: CION carries {tot_fv:,.0f}k; at other lenders' average marks {tot_avg:,.0f}k ({tot_avg-tot_fv:+,.0f}k = ${(tot_avg-tot_fv)/sh:+.2f}/share, {tot_avg/tot_fv-1:+.1%})")
print(f"  at the lowest other mark on each loan {tot_low:,.0f}k ({tot_low-tot_fv:+,.0f}k = ${(tot_low-tot_fv)/sh:+.2f}/share)")
ratio = pik_avg / pik_fv
print(f"of which in my PIK bucket: {pik_fv:,.0f}k, other lenders' marks are {ratio:.1%} of CION's")

U = rows('pik_unshared_largest.csv')
u = sum(float(r['cion_fair_value_k']) for r in U)
print(f"largest PIK loans with no other public holder: {len(U)} loans, {u:,.0f}k")

PIK_BUCKET = 405336  # 'Debt with PIK' at fair value, printed by book_quality.py
base_unshared = 0.75
blend = (pik_fv * ratio + (PIK_BUCKET - pik_fv) * base_unshared) / PIK_BUCKET
print(f"PIK bucket {PIK_BUCKET:,.0f}k: shared part at other lenders' marks ({ratio:.0%}), the rest at my old 75% base -> blended base recovery {blend:.1%}")
print(f"  shared PIK loans are {pik_fv/PIK_BUCKET:.0%} of the bucket; the unshared largest seven alone are {u/PIK_BUCKET:.0%}")

# Why the unshared loans keep a heavier haircut: they are worse paper, not just unchecked paper.
T = rows('pik_terms_2026_09_30.csv')
nocash = {r['portfolio_company'] for r in T if r['cash_rate'] == '—'} - {r['portfolio_company'] for r in T if r['cash_rate'] != '—'}
def is_nocash(name):
    return any(name.split()[0].lower() in n.lower() for n in nocash)
u_nc = sum(float(r['cion_fair_value_k']) for r in U if is_nocash(r['company']))
seen = set(); s_tot = s_nc = 0.0
for r in X:
    key = (r['company'], r['tranche'])
    if r['in_cion_pik_bucket'] != 'yes' or key in seen:
        continue
    seen.add(key); fv = float(r['cion_fair_value_k']); s_tot += fv
    if is_nocash(r['company']):
        s_nc += fv
print(f"pays no cash at all: {u_nc/u:.0%} of the unshared largest seven by value, {s_nc/s_tot:.0%} of the shared PIK loans")
