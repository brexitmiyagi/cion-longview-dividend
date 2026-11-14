# What CION's Longview stake says about the plant, and how CION got it.
from common import inputs, rows

I = inputs()
U = rows('longview_units.csv')
for r in U:
    u, c, f = float(r['units']), float(r['cost_k']), float(r['fair_value_k'])
    print(f"{r['period_end']}: {u:>11,.0f} units, cost {c:>7,.0f}k, mark {f:>8,.0f}k = ${f*1000/u:6.2f}/unit")
a, b = U[0], U[2]
du = float(b['units']) - float(a['units']); dc = float(b['cost_k']) - float(a['cost_k'])
print(f"2024 purchase (from Eaton Vance-managed funds per the FERC filing): +{du:,.0f} units for {dc:,.0f}k = ${dc*1000/du:.2f}/unit,"
      f" while CION marked its existing units at ${float(a['fair_value_k'])*1000/float(a['units']):.2f} (Dec 2023)")
last = U[-1]; per_unit = float(last['fair_value_k']) * 1000 / float(last['units'])
print(f"those units at the 30 Sep 2026 mark: {du*per_unit/1000:,.0f}k")

stake = I['cion_mseh_stake']; mw = I['longview_mw']
for p in ('2026-06-30', '2026-09-30'):
    f = float([r for r in U if r['period_end'] == p][0]['fair_value_k'])
    eq = f / stake
    print(f"{p}: CION mark {f:,.0f}k / ~{stake:.0%} stake = ~{eq/1000:,.0f}m for all of Mountain State's equity = ~${eq*1000/(mw*1000):,.0f}/kW on {mw:.0f} MW")
q3_div = 19444 - 5235
print(f"Q3 2026: CION's {q3_div:,.0f}k dividend / ~{stake:.0%} = ~{q3_div/stake/1000:,.0f}m paid out by the plant's owner in one quarter")

# Capacity revenue on the plant's 710 MW, before outages and bonuses/penalties; ELCC where PJM published it
for r in rows('pjm_capacity.csv'):
    elcc = float(r['coal_elcc']) if r['coal_elcc'] else 0.83
    rev = mw * elcc * float(r['rto_price_mw_day']) * 365 / 1e6
    tag = '' if r['coal_elcc'] else ' (2026/27 coal ELCC of 83% used as a stand-in)'
    print(f"{r['delivery_year']}: ${r['rto_price_mw_day']}/MW-day x {mw:.0f} MW x {elcc:.0%} = ~${rev:,.1f}m a year of capacity revenue{tag}")
