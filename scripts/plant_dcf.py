# Longview valued to retirement, on its own economics.
#
# Energy margin per MWh = power price - Longview's heat rate x coal price - variable O&M.
#  - power price: EIA's Short-Term Energy Outlook (Nov 2026) for the PJM Western hub, which runs
#    through 2027. After 2027 I use three paths, because nobody publishes a free forecast.
#  - heat rate: Longview's own, from EIA-923. Coal: what West Virginia coal plants paid in 2026
#    (EIA-923), since Longview's own fuel cost is redacted.
#  - Longview doesn't sell at the hub and doesn't run every hour, so I scale the hub-based margin
#    by a factor that makes 2025 match the PJM market monitor's APS-zone coal figure. I then test
#    that factor on Jan-Sep 2026, which it wasn't fitted to.
# Capacity revenue uses the three auctions already held, then a fade I have to assume.
# Fixed costs are the market monitor's coal avoidable cost, rising 2.5% a year.
# Discounted to 1 Jan 2027 at 10%. No debt (the 2020 exit loan left every fund's filing by 2023).
import os, csv
from common import inputs, rows

I = inputs()
MW = I['longview_mw']
M = {r['item']: float(r['value']) for r in rows('imm_coal_economics.csv')}
C = {r['item']: r['value'] for r in rows('eia_wv_coal_and_plant.csv')}
S = rows('eia_steo_nov2026.csv')
E = {r['period']: r for r in rows('eia923_longview.csv')}
CION_MARK = 99241e3
VOM = float(C['new_cp_vom'])

def hub(year, months=None):
    v = [float(r['pjm_west_hub_usd_mwh']) for r in S if r['year'] == str(year)]
    v = v[:months] if months else v
    return sum(v) / len(v)

def hr(period):
    return float(E[period]['coal_mmbtu']) / float(E[period]['coal_mwh'])  # MMBtu per MWh

# calibration on 2025
gen25 = float(E['2025']['coal_mwh']) + float(E['2025']['gas_mwh'])
m25 = hub(2025) - hr('2025') * float(C['wv_bituminous_delivered_cost_2025']) - VOM
imm25 = M['aps_new_cp_energy_net_revenue_2025'] * MW
k = imm25 / (m25 * gen25)
print(f"2025: hub ${hub(2025):.2f}, Longview heat rate {hr('2025')*1000:,.0f}, WV coal ${float(C['wv_bituminous_delivered_cost_2025']):.2f}/MMBtu -> margin ${m25:.2f}/MWh x {gen25/1e6:.2f}m MWh = ${m25*gen25/1e6:,.0f}m at the hub")
print(f"market monitor APS coal energy net revenue 2025 x 710 MW = ${imm25/1e6:,.1f}m, so location/dispatch factor k = {k:.3f}")

# out-of-sample test on Jan-Sep 2026
gen8 = float(E['2026']['coal_mwh']) + float(E['2026']['gas_mwh'])
gen9 = gen8 * 9 / 8  # September at the Jan-Aug monthly average
coal26 = float(C['wv_bituminous_delivered_cost_2026_jan_aug'])
m26 = hub(2026, 9) - hr('2026') * coal26 - VOM
mine9 = k * m26 * gen9
imm9 = M['aps_new_cp_energy_net_revenue_2026_jan_sep'] * MW
print(f"test, Jan-Sep 2026: hub ${hub(2026, 9):.2f} -> my energy margin ${mine9/1e6:,.1f}m vs market monitor ${imm9/1e6:,.1f}m ({mine9/imm9-1:+.0%})")
cap9 = (329.17 * 0.83 * 122 + 269.92 * 0.83 * 151) * MW
acr = M['coal_avoidable_cost'] * 365 * MW
eb9 = mine9 + cap9 - acr * 273 / 365
print(f"  Jan-Sep 2026 EBITDA on my numbers ${eb9/1e6:,.0f}m; owners paid out about ${19444e3/I['cion_mseh_stake']/1e6:,.0f}m")
print()

cap_known = {2027: (329.17 * 5 + 333.44 * 7) / 12, 2028: (333.44 * 5 + 325.00 * 7) / 12}  # calendar-year blends of the auctions held

def value(power_path, cap_after, retire=2040, rate=0.10, cf=0.80, elcc=0.85, coal=coal26, verbose=False):
    pv = 0.0
    for i, y in enumerate(range(2027, retire + 1)):
        price = power_path(y)
        gen = MW * 8760 * cf
        energy = k * (price - hr('2026') * coal - VOM) * gen
        if y in cap_known:
            capp = cap_known[y]
        elif y == 2029:
            capp = (325.00 * 5 + cap_after * 7) / 12
        else:
            capp = cap_after
        capacity = capp * elcc * 365 * MW
        fixed = acr * 1.025 ** (i + 1)
        cash = max(energy, 0) + capacity - fixed
        cash = max(cash, 0)  # an owner would mothball rather than run at a loss
        pv += cash / (1 + rate) ** (i + 0.5)
        if verbose:
            print(f"    {y}: power ${price:5.1f}  energy ${energy/1e6:6.1f}m  capacity ${capacity/1e6:5.1f}m  fixed ${fixed/1e6:5.1f}m  cash ${cash/1e6:6.1f}m")
    return pv

h27 = hub(2027)
paths = {
    'stays at the 2027 forecast': lambda y: h27,
    'fades to the 2025 level by 2030': lambda y: h27 if y <= 2027 else max(hub(2025), h27 - (h27 - hub(2025)) * (y - 2027) / 3),
    'fades to the 2023-24 level by 2030': lambda y: h27 if y <= 2027 else max((hub(2023) + hub(2024)) / 2, h27 - (h27 - (hub(2023) + hub(2024)) / 2) * (y - 2027) / 3),
}
print(f"EIA's forecast for the PJM Western hub: 2025 ${hub(2025):.2f}, 2026 ${hub(2026):.2f}, 2027 ${h27:.2f}")
print()
print("base: power fades to the 2025 level by 2030, capacity $250/MW-day after May 2029, retire end-2040, 10%:")
base = value(paths['fades to the 2025 level by 2030'], 250, verbose=True)
stake = I['cion_mseh_stake']
def line(label, v):
    print(f"  {label}: ${v/1e6:,.0f}m = ${v/(MW*1000):,.0f}/kW; CION ~15% = ${v*stake/1e6:,.1f}m = {v*stake/CION_MARK:.0%} of its mark")
line('base', base)
print()
print('sensitivities (one change at a time from the base):')
for name, p in paths.items():
    line(f"power {name}", value(p, 250))
for ca in (325, 150, 100):
    line(f"capacity after May 2029 ${ca}", value(paths['fades to the 2025 level by 2030'], ca))
for rt in (2035, 2045):
    line(f"retire end-{rt}", value(paths['fades to the 2025 level by 2030'], 250, retire=rt))
for rr in (0.08, 0.12):
    line(f"discount rate {rr:.0%}", value(paths['fades to the 2025 level by 2030'], 250, rate=rr))
for e in (0.80, 0.86):
    line(f"coal accreditation {e:.0%}", value(paths['fades to the 2025 level by 2030'], 250, elcc=e))
for c_ in (0.74, 0.87):
    line(f"capacity factor {c_:.0%}", value(paths['fades to the 2025 level by 2030'], 250, cf=c_))
print()
print('stake sensitivity (affects what CION owns, and every per-unit to per-kW conversion):')
for s in (0.14, 0.15, 0.16):
    units_total = 1495714 / s
    print(f"  {s:.0%}: CION's share of base ${base*s/1e6:,.1f}m ({base*s/CION_MARK:.0%} of mark); Virtus $40.00 = ${40*units_total/(MW*1000):,.0f}/kW; CION $66.35 = ${66.35*units_total/(MW*1000):,.0f}/kW")
print()
lo = value(paths['fades to the 2023-24 level by 2030'], 150, retire=2035)
hi = value(paths['stays at the 2027 forecast'], 325, retire=2045)
line('low (power to 2023-24 levels, capacity $150, retire 2035)', lo)
line('high (power stays at 2027 forecast, capacity $325, retire 2045)', hi)
