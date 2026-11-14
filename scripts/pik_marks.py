# Loan by loan (borrower by borrower), how CION marks debt once it pays in PIK.
# Data: data/cion_debt_by_borrower.csv (build_borrower_panel.py), nine quarters of XBRL.
# Marks are fair value over principal. "PIK" means at least one of the borrower's loans carries
# a PIK rate that quarter.
from collections import defaultdict
from common import rows

P = defaultdict(dict)
for r in rows('cion_debt_by_borrower.csv'):
    P[r['borrower_key']][r['quarter_end']] = {k: float(r[k]) for k in ('principal_k', 'cost_k', 'fair_value_k', 'max_pik_rate')}
Q = sorted({q for b in P.values() for q in b})
def mark(a):
    base = a['principal_k'] or a['cost_k']
    return a['fair_value_k'] / base if base else 0

print("borrowers paying PIK in at least four quarters, mark range and principal growth:")
at_par = []
for b, h in sorted(P.items(), key=lambda kv: -max(a['fair_value_k'] for a in kv[1].values())):
    pq = [q for q in Q if q in h and h[q]['max_pik_rate'] > 0]
    if len(pq) < 4:
        continue
    ms = [mark(h[q]) for q in pq]
    g = h[pq[-1]]['principal_k'] / h[pq[0]]['principal_k'] - 1 if h[pq[0]]['principal_k'] else 0
    print(f"  {b:26s} {len(pq)} quarters, marks {min(ms):.0%} to {max(ms):.0%}, principal {h[pq[0]]['principal_k']:8,.0f}k -> {h[pq[-1]]['principal_k']:8,.0f}k ({g:+.0%}), last fair value {h[pq[-1]]['fair_value_k']:8,.0f}k")
    if min(ms) >= 0.99 and pq[-1] == Q[-1]:
        at_par.append((b, len(pq), g, h[pq[-1]]['fair_value_k']))
print()
print("held at 99%+ of principal in every PIK quarter, and still held:")
for b, n, g, fv in at_par:
    print(f"  {b}: {n} quarters, principal {g:+.0%}, {fv:,.0f}k")
print()
for b in ('appalachian resource', 'homer city generation lp', 'trammell', 'cion/eagletree partners'):
    print(b)
    for q in Q:
        if q in P[b]:
            a = P[b][q]
            print(f"  {q}: principal {a['principal_k']:8,.0f}k, fair value {a['fair_value_k']:8,.0f}k, mark {mark(a):.0%}, PIK rate {a['max_pik_rate']:.2%}")
