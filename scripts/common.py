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
