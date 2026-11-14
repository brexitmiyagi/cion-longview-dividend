# What CION sold to its new joint venture, Senior Loan Fund Partners (SLFP), on 17 Sep 2026, and
# what it kept. The 10-Q (Note 7) lists SLFP's loans; I match each borrower to CION's own
# borrower-level history (data/cion_debt_by_borrower.csv) and compare CION's 30 June 2026 marks on
# those borrowers with the rest of its debt book. Marks are fair value over cost, so unfunded
# commitments (no cost, small negative fair value) don't distort them.
from common import inputs, rows
import statistics as st
I = inputs()
P = rows('cion_debt_by_borrower.csv')
J = rows('slfp_loans_2026_09_30.csv')
# SLFP's 19 borrowers, as they appear in my borrower panel (matched by name, checked by hand)
JK = ['american health staffing', 'anchor qea', 'aps', 'bds solutions intermedia', 'community tree service',
      'crosslink professional t', 'dependable', 'gold medal', 'ica foam', 'lift brands', 'metrc',
      'newbury franklin industr', 'playboy enterprises', 'shf', 'stengel hill architectur',
      'straine dental managemen', 'tactical air support', 'workgenius', 'xenon arc']
by = {}
for r in P:
    by.setdefault(r['borrower_key'], {})[r['quarter_end']] = r
def mark(r):
    c = float(r['cost_k'])
    return float(r['fair_value_k']) / c if c > 100 else None
Q = '2026-06-30'
book = []
for k, v in by.items():
    if Q in v and mark(v[Q]) is not None:
        hist = [mark(x) for qq, x in v.items() if qq <= Q and mark(x) is not None]
        book.append(dict(k=k, jv=k in JK, cost=float(v[Q]['cost_k']), fv=float(v[Q]['fair_value_k']),
                         m=mark(v[Q]), pik=float(v[Q]['max_pik_rate'] or 0) > 0, low=min(hist)))
print("CION's debt book on 30 Jun 2026, by borrower, fair value over cost:")
for lab, rs in (('borrowers whose loans went to SLFP', [b for b in book if b['jv']]), ('everything else', [b for b in book if not b['jv']])):
    c = sum(b['cost'] for b in rs); f = sum(b['fv'] for b in rs)
    print(f"  {lab}: {len(rs)} borrowers, cost {c:,.0f}k, marked at {f/c:.1%} of cost; "
          f"{sum(b['cost'] for b in rs if b['m'] < 0.95)/c:.0%} of cost marked below 95%; "
          f"{sum(b['cost'] for b in rs if b['pik'])/c:.0%} with a PIK feature; "
          f"{sum(1 for b in rs if b['low'] < 0.90)} ever marked below 90% since Sep 2024")
jp = sum(float(j['par_k']) for j in J); jf = sum(float(j['fair_value_k']) for j in J)
print(f"SLFP's loans on 30 Sep 2026: par {jp:,.0f}k, fair value {jf:,.0f}k = {jf/jp:.1%} of par")
c = f = 0
for k in JK:
    r = by[k].get('2026-09-30')
    if r and float(r['cost_k']) > 100:
        c += float(r['cost_k']); f += float(r['fair_value_k'])
print(f"CION still holds other pieces of the same borrowers: cost {c:,.0f}k at {f/c:.1%} of cost")
# The JV's capital, from Note 7
notes, pref, common_paid, common_fv = I['slfp_notes'], I['slfp_pref_liquidation'], I['slfp_sale_paid_in_jv_equity'], I['slfp_common_fv']
print(f"SLFP capital: notes {notes:,.0f}k (SOFR+4.75%, sold at 98.25), preferred {pref:,.0f}k (11.5% cumulative), CION's common {common_paid:,.0f}k")
print(f"  CION's common is first loss under {notes+pref:,.0f}k of senior capital: {jf/common_paid:.1f}x assets per dollar of CION equity")
print(f"  CION's common marked at {common_fv:,.0f}k on 30 Sep, {common_fv/common_paid-1:+.1%} on what it was paid in")
