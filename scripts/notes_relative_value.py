# CION's listed notes against other listed BDC notes. Prices are 13 Nov 2026 closes (Yahoo daily
# bars); coupons, maturities, call dates and asset coverage come from each issuer's latest 10-Q.
# These notes trade flat: they go ex-interest like a stock goes ex-dividend (Yahoo shows CICB
# ex-dates of 15 Dec, 13 Mar, 15 Jun and 15 Sep), so the close already includes interest built up
# since the last ex-date and the buyer gets the next coupon in full. Yields are on that price,
# quarterly compounding (common.note_yield). For notes above par with a dated call I also give
# the yield to that call; for notes above par that are callable any day I don't, since the
# premium can disappear on 30 days' notice.
# Left out: OFSSO (being redeemed after OFS's 28 Aug 2026 notice) and MFICL (no recent close).
# Hercules's coverage excludes its SBA debentures under an SEC order. PhenixFIN's is at 30 June
# (its September 10-K wasn't out); Saratoga's is at 31 August, its quarter end.
from datetime import date, timedelta
from common import rows, note_yield

TODAY = date(2026, 11, 13)
SETTLE = date(2026, 11, 13)  # next-day settlement, same as capital_structure.py

def ytm(price, coupon, end):
    return note_yield(price, coupon, end, SETTLE)

out = []
for r in rows('bdc_notes_2026_11_13.csv'):
    px = float(r['price_2026_11_13']); c = float(r['coupon'])
    mat = date.fromisoformat(r['maturity'])
    y = ytm(px, c, mat)
    ytw = y
    if px > 25 and r['first_call'] == 'now':
        ytw = None  # above par and callable any day: the yield can vanish, so no yield to worst
    elif px > 25 and r['first_call']:
        ytw = min(y, ytm(px, c, date.fromisoformat(r['first_call'])))
    out.append((r['ticker'], r['issuer'], mat, px, c, y, ytw, float(r['asset_coverage']), r['coverage_date']))

print("ticker | issuer | matures | 13 Nov close | coupon | yield to maturity | yield to worst | asset coverage")
for t, iss, m, px, c, y, w, ac, d in sorted(out, key=lambda x: x[2]):
    ws = f"{w:6.2%}" if w is not None else "  n/m "
    print(f"  {t:6s} {iss:22s} {m}  ${px:6.2f}  {c:.3%}  {y:6.2%}  {ws}  {ac:.0%} ({d})")

cion = [o for o in out if o[1].startswith('CION')]
near = [o for o in out if not o[1].startswith('CION') and date(2029, 1, 1) <= o[2] <= date(2031, 12, 31)]
avg = sum(o[5] for o in near) / len(near)
print()
print("CION's notes against other notes maturing 2029-2031 (yield to maturity):")
for o in near:
    flag = ', above par and callable now' if o[6] is None else (f', yield to first call {o[6]:.2%}' if o[6] < o[5] - 1e-6 else '')
    print(f"  {o[0]} {o[2]} {o[5]:.2%}{flag}, coverage {o[7]:.0%}")
for o in cion:
    print(f"  {o[0]} {o[5]:.2%}: {(o[5]-avg)*1e4:+.0f}bp vs their average of {avg:.2%}")
low = sorted(out, key=lambda x: x[7])
print("asset coverage, lowest first: " + ", ".join(f"{o[1].split()[0]} {o[7]:.0%}" for o in low if o[0] not in ('CICC', 'OXSQH', 'GECCH')))

# Spread over Treasuries at the same maturity. The Treasury curve is par yields, compounded
# twice a year, so I convert each note's quarterly-compounded yield first.
T = [(float(r['tenor_years']), float(r['par_yield_pct']) / 100) for r in rows('treasury_par_curve_2026_11_13.csv')]
def ust(years):
    for (t0, y0), (t1, y1) in zip(T, T[1:]):
        if t0 <= years <= t1:
            return y0 + (y1 - y0) * (years - t0) / (t1 - t0)
    return T[-1][1]
print()
print("spread over the matched-maturity Treasury (yield converted to semiannual):")
for o in sorted(out, key=lambda x: x[2]):
    yrs = (o[2] - SETTLE).days / 365.25
    sa = 2 * ((1 + o[5] / 4) ** 2 - 1)
    print(f"  {o[0]:6s} {yrs:4.1f} years: {sa:.2%} vs Treasury {ust(yrs):.2%} = {(sa-ust(yrs))*1e4:4.0f}bp")
LQ = rows('notes_liquidity.csv')
print("trading, last three months:")
for r in LQ:
    print(f"  {r['ticker']}: about ${float(r['avg_daily_dollar_volume_3m'])/1000:,.0f}k a day, no trades on {r['days_with_no_trades_3m']} of {r['trading_days']} days")
print("rating: CION's 10-Q says several of its private notes are rated investment grade; it gives no rating for CICB or CICC")
