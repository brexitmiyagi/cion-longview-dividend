# Same Longview units, different funds, different prices.
# CION isn't the only SEC-registered fund that owns Longview Intermediate Holdings units.
# Eaton Vance funds (including the Brighthouse portfolio Eaton Vance runs), a Virtus Seix fund
# and the City National Rochdale Fixed Income Opportunities Fund (which calls its units
# "Longview Power, LLC 7/20", the July 2020 exit equity) report theirs in N-PORT and N-CSR filings. This lines their per-unit marks up against
# CION's on the same quarter ends, and against the price CION paid in 2024.
import os, csv
from common import rows, inputs

HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()

marks = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'longview_third_party_marks.csv'))))
cion = {r['period_end']: (float(r['units']), float(r['fair_value_k']) * 1000, float(r['cost_k']) * 1000) for r in rows('longview_units.csv')}
extra = {'2023-09-30': (653989, 21863000, 2704000), '2024-03-31': (653989, 20408000, 2704000)}  # CION 10-Qs, Q3 2023 and Q1 2024
cion.update(extra)


def per_unit(r):
    return float(r['fair_value_usd']) / float(r['units'])


print('per-unit marks, other funds')
for r in marks:
    if r['period_end'] >= '2023-09':
        print(f"  {r['period_end']}  {r['fund'][:48]:48s} {int(float(r['units'])):>9,} units  ${per_unit(r):6.2f}  ({r['form']})")
print()
print('CION per-unit marks')
for d in sorted(cion):
    u, v, c = cion[d]
    print(f"  {d}  {int(u):>9,} units  ${v/u:6.2f}")
print()

# the side-by-side quarter ends
def other_on(prefix, who):
    for r in marks:
        if r['period_end'].startswith(prefix) and who in r['fund']:
            return per_unit(r)
pairs = [('2023-12', '2023-12-31'), ('2024-06', '2024-06-30'), ('2024-12', '2024-12-31'), ('2025-06', '2025-06-30'), ('2025-09', '2025-09-30'), ('2025-12', '2025-12-31'), ('2026-06', '2026-06-30')]
for p, cd in pairs:
    u, v, c = cion[cd]
    c_px = v / u
    vs = other_on(p, 'Virtus')
    bh = other_on(p, 'Brighthouse')
    line = f"{cd}: CION ${c_px:.2f}"
    if vs: line += f" | Virtus Seix ${vs:.2f} (CION {c_px/vs:.1f}x)"
    if bh: line += f" | Brighthouse/Eaton Vance ${bh:.2f} (CION {c_px/bh:.1f}x)"
    cn = other_on(p, 'City National')
    if cn: line += f" | City National Rochdale ${cn:.2f} (CION {c_px/cn:.1f}x)"
    print(line)
cn = [r for r in marks if 'City National' in r['fund']]
print(f"City National Rochdale held {int(float(cn[0]['units'])):,} units at the end of 2024 and {int(float(cn[1]['units'])):,} from March 2025: {int(float(cn[0]['units'])-float(cn[1]['units'])):,} units left the fund in Q1 2025, at a time it marked them at ${per_unit(cn[0]):.2f}")
same = all(abs(per_unit(r) - (other_on(r['period_end'][:7], 'Virtus') or -1)) < 0.005 for r in cn if other_on(r['period_end'][:7], 'Virtus'))
print(f"City National Rochdale's per-unit mark equals Virtus's at every quarter end both report: {same}. That points to the same outside price source, so it confirms Virtus's price rather than adding an independent one.")
print()

# the 2024 purchase: units and cost added between 31 Mar and 30 Jun 2024
u0, v0, c0 = cion['2024-03-31']
u1, v1, c1 = cion['2024-06-30']
bought, paid = u1 - u0, c1 - c0
mark_after = v1 / u1
uplift = bought * mark_after - paid
nav_q2_2024 = 860806000  # CION 10-Q Q2 2024 balance sheet
print(f"Q2 2024: CION added {int(bought):,} units for ${paid/1e3:,.0f}k = ${paid/bought:.2f} a unit,"
      f" and marked them at ${mark_after:.2f} on 30 Jun 2024 = ${bought*mark_after/1e3:,.0f}k;"
      f" gain on day one ${uplift/1e3:,.0f}k = {uplift/nav_q2_2024:.1%} of 30 Jun 2024 NAV")
u2, v2, c2 = cion['2024-09-30']
print(f"Q3 2024: added {int(u2-u1):,} more units for ${(c2-c1)/1e3:,.0f}k = ${(c2-c1)/(u2-u1):.2f} a unit")
print()

# what CION's stake is worth at the Virtus mark
u, v, c = cion['2026-09-30']
div_per_unit = 14209000 / u  # Q3 2026 Longview dividend to CION, per unit
vs_jun = other_on('2026-06', 'Virtus')
ex_div = vs_jun - div_per_unit
sh = I['shares_outstanding_2026_09_30']
print(f"Q3 2026 dividend per unit ${div_per_unit:.2f}; Virtus 30 Jun 2026 mark ${vs_jun:.2f} less that = ${ex_div:.2f}"
      f" = {ex_div/(v/u):.0%} of CION's 30 Sep mark of ${v/u:.2f}")
print(f"CION's stake at ${ex_div:.2f} a unit: ${u*ex_div/1e3:,.0f}k vs mark ${v/1e3:,.0f}k;"
      f" difference ${(v-u*ex_div)/1e3:,.0f}k = ${(v-u*ex_div)/sh:.2f} a share = {(v-u*ex_div)/sh/I['price_2026_11_13']:.0%} of the share price")

print()
print("CION's disclosed $ per kW input for the line that matches Longview's fair value")
for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'cion_longview_valuation_input.csv'))):
    print(f"  {r['period_end']}: ${float(r['usd_per_kw']):,.2f} per kW, fair value {float(r['fair_value_k']):,.0f}k")
lo, hi = u * ex_div, u * vs_jun
print(f"range at the Virtus mark: ${lo/1e3:,.1f}k to ${hi/1e3:,.1f}k; gap to CION's mark ${(v-hi)/sh:.2f} to ${(v-lo)/sh:.2f} a share"
      f" ({(v-hi)/sh/I['price_2026_11_13']:.0%} to {(v-lo)/sh/I['price_2026_11_13']:.0%} of the price)")
