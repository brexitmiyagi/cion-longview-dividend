import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')


def inputs():
    out = {}
    with open(os.path.join(DATA, 'inputs.csv')) as f:
        for r in csv.DictReader(f):
            out[r['item']] = float(r['value'])
    return out


def rows(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def incentive_fee(pre, net_assets, I):
    """CION's income incentive fee: nothing up to 1.625% of net assets a quarter,
    100% of the excess up to 1.970%, then 17.5% of everything."""
    h = I['hurdle_rate_quarterly'] * net_assets
    c = I['catchup_rate_quarterly'] * net_assets
    if pre <= h:
        return 0.0
    if pre <= c:
        return pre - h
    return (c - h) + I['incentive_rate'] * (pre - c)


def note_yield(price, coupon, maturity, settle, par=25.0):
    """Yield (quarterly compounding, annualised) on a $25 listed note. Coupons are paid
    quarterly, counted back from maturity. The quoted price is treated as the full price
    paid, with no separate accrued interest, the same way for every note."""
    from datetime import date
    def back(d, months):
        y, m = d.year, d.month - months
        while m <= 0:
            m += 12; y -= 1
        day = min(d.day, [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
        return date(y, m, day)
    flows, k = [], 0
    while True:
        d = back(maturity, 3 * k)
        if d <= settle:
            break
        flows.append((d, par * coupon / 4 + (par if k == 0 else 0)))
        k += 1
    lo, hi = -0.5, 1.0
    for _ in range(200):
        y = (lo + hi) / 2
        pv = sum(cf / (1 + y / 4) ** (4 * (d - settle).days / 365.25) for d, cf in flows)
        lo, hi = (y, hi) if pv > price else (lo, y)
    return y


# SOFR on the futures curve, quarter by quarter, and what it does to net interest income.
# Each three-month SOFR futures contract's rate is placed at the middle of its reference period,
# with straight lines in between. The shift from the 3.88% base rate in CION's 10-Q rate table
# goes through that table (straight lines between its rows) and is spread evenly over the
# quarter. Loans reset with a lag of one to three months, which I ignore.
QUARTER_MID = {'Q4 2026': '2026-11-15', 'Q1 2027': '2027-02-14', 'Q2 2027': '2027-05-16',
               'Q3 2027': '2027-08-15', 'Q4 2027': '2027-11-15'}
RATE_TABLE_BASE = 0.0388

def sofr_curve():
    import datetime as dt
    pts = []
    for r in rows('sofr_futures_2026_11_13.csv'):
        start = dt.date.fromisoformat(r['reference_quarter_start'])
        pts.append((start + dt.timedelta(days=45), (100 - float(r['last_2026_11_13'])) / 100))
    out = {}
    for q, ds in QUARTER_MID.items():
        d = dt.date.fromisoformat(ds)
        for (d0, r0), (d1, r1) in zip(pts, pts[1:]):
            if d0 <= d <= d1:
                out[q] = r0 + (r1 - r0) * (d - d0).days / (d1 - d0).days
                break
    return out

def nii_change_k(bp):
    t = sorted([(0, 0.0)] + [(int(r['change_bp']), float(r['net_interest_income_change_k'])) for r in rows('rate_sensitivity_2026_09_30.csv')])
    for (b0, v0), (b1, v1) in zip(t, t[1:]):
        if b0 <= bp <= b1:
            return v0 + (v1 - v0) * (bp - b0) / (b1 - b0)
    raise ValueError(bp)

def curve_add(extra_bp=0.0):
    """Quarterly addition to pre-incentive NII (thousands) for SOFR on the futures curve,
    plus an optional parallel shift of the curve."""
    return {q: nii_change_k((r - RATE_TABLE_BASE) * 1e4 + extra_bp) / 4 for q, r in sofr_curve().items()}
