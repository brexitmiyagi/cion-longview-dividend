# An outside-in value for the Longview plant, built from public data only, so it can be
# set against CION's mark and the Virtus Seix fund's mark.
#
# EBITDA = energy net revenue + capacity revenue - avoidable fixed costs, all per MW of
# installed capacity, times 710 MW. Energy net revenue and avoidable costs are the PJM
# market monitor's figures for coal (APS zone, where Longview sits per AEP's FERC
# application). Capacity revenue is the auction price times PJM's coal accreditation.
# The multiples are my judgment, informed by recent thermal deals (data/thermal_comps.csv).
import os, csv
from common import inputs, rows

HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()
M = {r['item']: float(r['value']) for r in rows('imm_coal_economics.csv')}
mw = I['longview_mw']
stake = I['cion_mseh_stake']
units = 1495714  # CION's units on 30 Sep 2026 (data/longview_units.csv)
cion_mark = 99241e3

print('what the plant did (EIA-923)')
for r in rows('eia923_longview.csv'):
    n = float(r['months']); mwh = float(r['coal_mwh']) + float(r['gas_mwh'])
    cf = mwh / (mw * 8760 * n / 12)
    hr = float(r['coal_mmbtu']) * 1000 / float(r['coal_mwh'])
    print(f"  {r['period']} ({int(n)} months): {mwh/1e6:.2f} million MWh, capacity factor {cf:.0%}, coal heat rate {hr:,.0f} Btu/kWh"
          f" (market monitor's new coal plant assumes {M['new_cp_heat_rate']:,.0f})")
print()

cap = {r['delivery_year']: (float(r['rto_price_mw_day']), float(r['coal_elcc']) if r['coal_elcc'] else 0.83) for r in rows('pjm_capacity.csv')}
def cap_rev(dy):
    p, e = cap[dy]
    return p * e * 365
acr = M['coal_avoidable_cost'] * 365
print(f"avoidable fixed costs for coal: ${M['coal_avoidable_cost']}/MW-day = ${acr:,.0f} per MW-year")
for dy in ('2026/2027', '2027/2028', '2028/2029'):
    print(f"capacity revenue {dy}: ${cap_rev(dy):,.0f} per MW-year")
print()

# nine months of 2026, rebuilt and set against what the owners actually took out
e9 = M['aps_new_cp_energy_net_revenue_2026_jan_sep']
c9 = cap['2025/2026'][0] * 0.83 * 151 + cap['2026/2027'][0] * cap['2026/2027'][1] * 122  # Jan-May at 2025/26, Jun-Sep at 2026/27
a9 = acr * 273 / 365
eb9 = (e9 + c9 - a9) * mw
paid9 = 19444e3 / stake  # CION's 2026 Longview dividends grossed up for its ~15% stake
print(f"Jan-Sep 2026 estimate: energy ${e9*mw/1e6:,.1f}m + capacity ${c9*mw/1e6:,.1f}m - fixed costs ${a9*mw/1e6:,.1f}m = EBITDA ~${eb9/1e6:,.0f}m;"
      f" the owners paid out ~${paid9/1e6:,.0f}m over the same nine months")
print("  (2025/26 coal accreditation not in my data; 83% used as a stand-in)")
print()

# two run-rate cases on 2026/27 capacity revenue
cases = {
    'A: 2025 energy margins': M['aps_new_cp_energy_net_revenue_2025'],
    'B: 2026 energy margins (Jan-Sep x 4/3)': e9 * 4 / 3,
}
eb = {}
for k, e in cases.items():
    eb[k] = (e + cap_rev('2026/2027') - acr) * mw
    print(f"{k}: energy ${e:,.0f}/MW-yr -> EBITDA ${eb[k]/1e6:,.1f}m a year")
print()

total_units = units / stake
print(f"plant equity implied by marks (~{stake:.0%} stake, ~{total_units/1e6:.2f}m units in total):")
for name, px in (('CION 30 Jun 2026', 72.74), ('CION 30 Sep 2026', 66.35), ('Virtus 30 Jun 2026', 40.00), ('Virtus less Q3 dividend', 30.50)):
    eq = px * total_units
    print(f"  {name}: ${px:.2f}/unit -> ${eq/1e6:,.0f}m = ${eq/(mw*1000):,.0f}/kW")
print(f"  CION's own disclosed input on 30 Sep 2026: $938/kW")
print()

print('value from the two cases (equity = enterprise value; the 2020 exit term loan left every fund filing by early 2023):')
out = {}
for k, e in eb.items():
    for x in (4, 5, 6):
        ev = e * x
        out[(k[0], x)] = ev
        print(f"  {k[:1]} at {x}x: ${ev/1e6:,.0f}m = ${ev/(mw*1000):,.0f}/kW; CION's ~15% = ${ev*stake/1e6:,.1f}m = {ev*stake/cion_mark:.0%} of its 30 Sep mark")
base = (out[('A', 5)] + out[('B', 5)]) / 2
print(f"base (average of A and B at 5x): ${base/1e6:,.0f}m = ${base/(mw*1000):,.0f}/kW; CION's share ${base*stake/1e6:,.1f}m = {base*stake/cion_mark:.0%} of its mark")
print(f"multiple of case A EBITDA implied by CION's $938/kW: {938*mw*1000/eb['A: 2025 energy margins']:.1f}x; of case B: {938*mw*1000/eb['B: 2026 energy margins (Jan-Sep x 4/3)']:.1f}x")
print()

# the 2024-25 gap between CION's $/kW input and its mark
print("CION mark vs its own $ per kW input (equity at ~15% minus input x 710 MW):")
for r in rows('cion_longview_valuation_input.csv'):
    eq = float(r['fair_value_k']) * 1000 / stake
    gap = eq - float(r['usd_per_kw']) * mw * 1000
    print(f"  {r['period_end']}: mark implies ${eq/1e6:,.0f}m, input x MW ${float(r['usd_per_kw'])*mw/1e3:,.0f}m, difference ${gap/1e6:,.0f}m")
