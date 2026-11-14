# Twelve-month total return, CION common against CICB (the 7.50% notes due 30 Dec 2029), in my
# bear, base and bull cases, from the 13 Nov 2026 closes.
#
# Common: the case's value in twelve months (nav_model.py, half on the peer line and half on
# today's discount carrying forward) plus distributions with record dates in the year: $0.10 for
# December 2026 (declared), then the 2027 base of 25 cents a quarter paid monthly, ten months
# through October 2027. In the bear case the base drops to 20 cents a quarter from July 2027.
#
# CICB: coupon plus the price change if its yield doesn't move, which pulls it toward par, plus a
# change in spread: bear +200bp, base unchanged, bull -50bp. Those spread moves are my assumption.
# Price change for a spread move uses modified duration. A call at par from 30 Dec 2026 would be
# a gain from $24.46, so it's ignored here.
import io, os, runpy, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
with contextlib.redirect_stdout(io.StringIO()):
    FR = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
VAL = FR['VAL']; I = FR['I']
px = I['price_2026_11_13']

DIST = {'bear': 0.10 + 6 * 0.25 / 3 + 4 * 0.20 / 3, 'base': 0.10 + 10 * 0.25 / 3, 'bull': 0.10 + 10 * 0.25 / 3}

from datetime import date
from common import note_yield
price, cpn, par = 24.46, 0.075, 25.0
MAT = date(2029, 12, 30); S0 = date(2026, 11, 13); S1 = date(2027, 11, 13)
coupon = par * cpn   # four quarterly coupons fall in the year: Dec 30, Mar 30, Jun 30, Sep 30
def price_at(y, settle):
    # same convention as common.note_yield: the quoted price is the full price, coupons quarterly back from maturity
    flows = []; k = 0
    while True:
        m = MAT.month - 3 * k; yr = MAT.year
        while m <= 0:
            m += 12; yr -= 1
        d = date(yr, m, min(MAT.day, 30 if m in (4, 6, 9, 11) else 28 if m == 2 else 31))
        if d <= settle:
            break
        flows.append((d, par * cpn / 4 + (par if k == 0 else 0))); k += 1
    return sum(cf / (1 + y / 4) ** (4 * (d - settle).days / 365.25) for d, cf in flows)
ytm = note_yield(price, cpn, MAT, S0)
SPREAD = {'bear': 0.02, 'base': 0.0, 'bull': -0.005}
W = {'bear': 0.25, 'base': 0.50, 'bull': 0.25}
tb = 0.0465   # 1-year Treasury par yield, 13 Nov 2026 (data/treasury_par_curve_2026_11_13.csv)

print(f"CICB yield at ${price}: {ytm:.2%} (quarterly compounding)")
rows_ = {}
for case in ('bear', 'base', 'bull'):
    c_tr = (VAL[case] + DIST[case]) / px - 1
    p1 = price_at(ytm + SPREAD[case], S1)
    n_tr = (p1 + coupon) / price - 1
    rows_[case] = (c_tr, n_tr)
    print(f"  {case} ({W[case]:.0%}): common ${VAL[case]:.2f} + ${DIST[case]:.2f} distributions = {c_tr:+.1%}; CICB ${p1:.2f} + ${coupon:.3f} coupons = {n_tr:+.1%}")
ec = sum(W[k] * v[0] for k, v in rows_.items()); en = sum(W[k] * v[1] for k, v in rows_.items())
print(f"weighted 25/50/25: common {ec:+.1%}, CICB {en:+.1%}")
# Risk from what the two have actually done, not from my scenarios: realised volatility since
# CICB listed (realized_risk.py), against my expected returns.
with contextlib.redirect_stdout(io.StringIO()):
    RR = runpy.run_path(os.path.join(HERE, 'realized_risk.py'))
vc, vn = RR['ST']['CION common']['vol'], RR['ST']['CICB']['vol']
print(f"expected return over a one-year Treasury ({tb:.2%}) per unit of realised volatility: common {(ec-tb)/vc:.2f} ({vc:.1%} vol), CICB {(en-tb)/vn:.2f} ({vn:.1%} vol)")
for pb in [x / 100 for x in range(0, 76)]:
    w = {'bear': pb, 'bull': 0.25, 'base': 0.75 - pb}
    if sum(w[k] * (rows_[k][1] - rows_[k][0]) for k in w) >= 0:
        print(f"CICB matches the common on expected return once the bear case gets {pb:.0%} (bull held at 25%)")
        break
# If CION calls CICB at par on 30 Dec 2026 (it can, from that date), a holder gets par plus the
# December coupon, then has to reinvest.
called = (par + par * cpn / 4) / price - 1
print(f"if CICB is called on 30 Dec 2026: ${par + par*cpn/4:.2f} against ${price}, {called:+.1%} in seven weeks, then reinvest")
