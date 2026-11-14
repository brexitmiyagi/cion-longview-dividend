# Quarterly NII and NAV, Q4 2026 to Q4 2027, in three cases, and a target from what the
# market pays other BDCs for their earnings.
#
# Each quarter: NAV + NII - distributions - credit losses (+ what buybacks below NAV add per
# share). NII starts from the run-rate in core_earnings_bridge.py.
#
# Credit losses (net realized and unrealized, Longview taken out):
#   2025: -113.7m reported, of which Longview's mark rose 53.5m, so -167.2m for the rest, 41.8m a quarter
#   2026, nine months: -35.0m reported, Longview -6.4m, so -28.5m, 9.5m a quarter
# Base uses the 2026 pace, bear the average of all seven quarters (28.0m), bull half the 2026 pace.
# Lost income on losses: the written-off assets stop earning, at 8% a year (my estimate).
#
# Longview: AEP closes at the end of Q1 2027. Proceeds as a share of CION's 30 Sep mark are the
# same as in valuation.py (bear 41%, base 80%, bull 154%); the gap to the mark hits NAV at closing.
# Dividends before closing: the first-half 2026 average. The cash goes half to work in Q2 2027 and
# fully in Q3: buybacks up to 1.35x net leverage at $6.14, the rest repays SOFR+4.75% notes.
#
# Rates: SOFR follows the futures curve of 13 Nov 2026 (common.curve_add), rising from about 4.0%
# in Q4 2026 to about 4.8% in Q4 2027. run(case, rate_add={}) gives the old flat-rate version.
#
# Distributions: $0.30 in Q4 2026, $0.25 after (what CION has declared and guided). The model
# doesn't cut them; whether they get cut is the question it answers.
import io, os, runpy, contextlib
from common import inputs, rows, incentive_fee, curve_add, sofr_curve

HERE = os.path.dirname(os.path.abspath(__file__))
I = inputs()
with contextlib.redirect_stdout(io.StringIO()):
    B = runpy.run_path(os.path.join(HERE, 'core_earnings_bridge.py'))
core = B['run']
sofr = I['sofr_3m_2026_09_30']
px = I['price_2026_11_13']
lv = 99241
lv_div = (I['longview_dividend_q1_2026'] + I['longview_dividend_q2_2026']) / 2
L = {r['quarter']: r for r in rows('credit_losses_by_quarter.csv')}
loss25 = (float(L['FY 2025']['net_realized_and_unrealized_k']) - float(L['FY 2025']['longview_mark_change_k'])) / 4
loss26 = sum(float(L[q]['net_realized_and_unrealized_k']) - float(L[q]['longview_mark_change_k']) for q in ('Q1 2026', 'Q2 2026', 'Q3 2026')) / 3
loss_all = (loss25 * 4 + loss26 * 3) / 7
print(f"credit losses ex-Longview a quarter: 2025 {loss25:,.0f}k, 2026 {loss26:,.0f}k, seven-quarter average {loss_all:,.0f}k")
known = {q: float(L[q]['net_realized_and_unrealized_k']) - float(L[q]['longview_mark_change_k']) for q in ('Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026', 'Q3 2026')}
h1 = float(L['Q1 2025']['net_realized_and_unrealized_k']) + float(L['Q2 2025']['net_realized_and_unrealized_k']) - 17989
print(f"  by quarter ex-Longview: H1 2025 {h1:,.0f}k (Q1 alone between {float(L['Q1 2025']['net_realized_and_unrealized_k'])-17989:,.0f}k and {float(L['Q1 2025']['net_realized_and_unrealized_k']):,.0f}k), " + ", ".join(f"{q} {v:,.0f}k" for q, v in known.items()))
print(f"  quarters at the bear pace ({loss_all:,.0f}k) or worse: Q1 2025 and " + ", ".join(q for q, v in known.items() if v <= loss_all) + "; the other three (Q2 2025, Q2 2026, Q3 2026) at the base pace or better")
CASES = {'bear': dict(loss=loss_all, lv=0.41), 'base': dict(loss=loss26, lv=0.80), 'bull': dict(loss=loss26 / 2, lv=1.54)}
Q = ['Q4 2026', 'Q1 2027', 'Q2 2027', 'Q3 2027', 'Q4 2027']
CURVE = curve_add()
DIST = {'Q4 2026': 0.30}

def run(case, verbose=False, rate_add=None):
    c = CASES[case]
    na = I['net_assets_2026_09_30']; sh = I['shares_outstanding_2026_09_30'] / 1000
    cash = 0.0; deployed_buy = deployed_rest = 0.0; lost = 0.0; out = []
    plan_buy = plan_rest = 0.0
    for q in Q:
        pre = core - lost * 0.08 / 4
        if q in ('Q4 2026', 'Q1 2027'):
            pre += lv_div
        else:
            share = 0.5 if q == 'Q2 2027' else 1.0
            add_buy = plan_buy * share - deployed_buy; add_rest = plan_rest * share - deployed_rest
            if add_buy > 0:
                na -= add_buy; sh -= add_buy / px; deployed_buy += add_buy; cash -= add_buy
            deployed_rest += max(add_rest, 0); cash -= max(add_rest, 0)
            pre += deployed_rest * (sofr + 0.0475) / 4 + cash * sofr / 4
        ra = CURVE if rate_add is None else rate_add
        if ra:
            pre += ra[q]
        fee = incentive_fee(pre, na, I)
        nii = pre - fee
        d = DIST.get(q, 0.25) * sh
        na += nii - d + c['loss']
        lost += -c['loss']
        if q == 'Q1 2027':  # AEP closes at quarter end
            proceeds = lv * c['lv']
            na += proceeds - lv
            cash = proceeds
            net_debt = I['debt_principal'] - I['cash'] - I['short_term_investments'] - proceeds
            plan_buy = max(0.0, min((I['leverage_target_high'] * na - net_debt) / (1 + I['leverage_target_high']), I['buyback_authorization_remaining'], proceeds))
            plan_rest = proceeds - plan_buy
        out.append(dict(q=q, nii_ps=nii / sh, dist_ps=d / sh, nav_ps=na / sh, na=na, sh=sh, nii=nii))
        if verbose:
            print(f"  {q}: NII ${nii/sh:.3f}  distribution ${d/sh:.2f}  credit losses ${c['loss']/sh:+.2f}  NAV/share ${na/sh:.2f}  shares {sh/1000:.1f}m")
    return out

res = {}
for case in CASES:
    print(f"{case}: credit losses {CASES[case]['loss']:,.0f}k a quarter, Longview at {CASES[case]['lv']:.0%} of mark")
    res[case] = run(case, verbose=True)
print()

# What other BDCs trade at for their earnings: price/NAV against NII return on NAV (annualised
# nine-month NII over 30 Sep net assets), listed peers, 13 Nov prices.
#
# Two problems with using that line on CION as it stands.
# 1. It credits PIK income in full, and CION's PIK ($11.4m in Q3) is more than its forward NII.
#    Across the peers the market doesn't discount PIK (adding PIK share to the regression doesn't
#    help), so the discount has to come from my view of CION's PIK, not from the peers. I count
#    PIK income at the same recovery I use for the PIK loans: 55% bear, 79% base, 90% bull.
# 2. Hercules (a venture lender at 1.29x NAV) and Rand (mostly equity) are different businesses,
#    and Hercules alone moves the line a lot. I fit the line without both.
# NAV: I used to restate CION's PIK bucket to other lenders' marks (about 8% lower where I can
# compare, pik_cross_marks.py). cross_mark_followup.py found no sign that the gap predicts later
# markdowns, so the base case no longer takes it. It's still printed as an alternative.
import numpy as np
ALL = rows('peer_bdcs_2026_09.csv')
def stats(r):
    nav = float(r['nav_per_share_2026_09_30']); s = float(r['shares_2026_09_30'])
    nii = float(r['nii_9m']) * 4 / 3; pik = float(r['pik_9m']) * 4 / 3
    return dict(t=r['ticker'], pnav=float(r['price_2026_11_13']) / nav, roe=nii / (nav * s), roex=(nii - pik) / (nav * s),
                piksh=float(r['pik_9m']) / float(r['total_investment_income_9m']))
S = [stats(r) for r in ALL]
cion = [x for x in S if x['t'] == 'CION'][0]
def fit(excl, cols):
    pp = [x for x in S if x['t'] != 'CION' and x['t'] not in excl]
    X = np.array([[1] + [x[c] for c in cols] for x in pp]); y = np.array([x['pnav'] for x in pp])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    r2 = 1 - ((y - X @ coef) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return coef, r2, len(pp)
print("peer line, P/NAV on NII/NAV, and how much it depends on which peers:")
for excl in ((), ('HTGC',), ('RAND',), ('HTGC', 'RAND')):
    for cols in (['roe'], ['roe', 'piksh']):
        coef, r2, n = fit(excl, cols)
        print(f"  without {', '.join(excl) or 'nobody'} ({n} peers), on {' + '.join(cols)}: " + ' '.join(f'{v:.2f}' for v in coef) + f", R-squared {r2:.2f}")
(a1, b1), r21, n1 = fit(('HTGC', 'RAND'), ['roe'])
(a0, b0), r20, n0 = fit((), ['roe'])
print(f"used: P/NAV = {a1:.2f} + {b1:.2f} x NII/NAV, {n1} peers, R-squared {r21:.2f}. Earnings explain about a quarter of how these BDCs are priced.")
print(f"CION today: NII/NAV {cion['roe']:.1%}, P/NAV {cion['pnav']:.2f}; the line says {a1+b1*cion['roe']:.2f}x")
pik_q = I['q3_pik_income']
PIKR = {'bear': 0.55, 'base': 0.79, 'bull': 0.90}
PIK_BUCKET = 405336
restate_alt = PIK_BUCKET * (1 - 0.918)   # pik_cross_marks.py: other lenders' marks are 91.8% of CION's on shared PIK loans
restate = 0.0                            # not in the base case any more
print(f"NAV restated to other lenders' marks on the PIK bucket (alternative only): -{restate_alt:,.0f}k")
print()
print("12-month target: the market will be looking at the 30 Sep 2027 NAV (10-Q out early November 2027),")
print("valued on Q3 2027 NII annualised, the same reported basis the peer line uses.")
# One target, set by data. The peer line says what CION is worth if the market pays it what it
# pays other BDCs for the same earnings. CION trades well below the line. discount_persistence.py
# checks how much of such a gap is still there a year later across the 16 peers since 2024: about
# 93%. So the target carries that share of today's gap forward. NII stays on the reported basis
# (PIK in full), because today's gap is measured on that basis and already holds the market's view
# of CION's PIK; haircutting PIK as well would count that view twice (printed below anyway).
with contextlib.redirect_stdout(io.StringIO()):
    DP = runpy.run_path(os.path.join(HERE, 'discount_persistence.py'))
KEEP, KEEP_LO, KEEP_HI = DP['slope'], DP['lo'], DP['hi']
resid = cion['pnav'] - (a1 + b1 * cion['roe'])
pp = [x for x in S if x['t'] not in ('CION', 'HTGC', 'RAND')]
Xp = np.array([[1, x['roe']] for x in pp]); yp = np.array([x['pnav'] for x in pp])
s2 = ((yp - Xp @ np.array([a1, b1])) ** 2).sum() / (len(pp) - 2); XtXi = np.linalg.inv(Xp.T @ Xp)
T80 = 1.345   # t with 14 degrees of freedom, 80% two-sided
print(f"CION today: {cion['pnav']:.2f}x NAV against {a1+b1*cion['roe']:.2f}x on the line, a gap of {resid:+.2f}x; share of such gaps still there a year later {KEEP:.2f} (80% range {KEEP_LO:.2f} to {KEEP_HI:.2f})")
def value(m_line, nav_ps, keep=None):
    return (m_line + (KEEP if keep is None else keep) * resid) * nav_ps
tg = {}; detail = {}; VAL = {}
# The line can pay a worse case a higher multiple: in the bear case NAV falls faster than NII, so
# NII/NAV rises. No market pays more for a BDC that just lost more than a quarter of its book, so the bear
# multiple is capped at the base case's, and the bull multiple floored at it.
_rb = [x for x in res['base'] if x['q'] == 'Q3 2027'][0]
M_BASE = a1 + b1 * _rb['nii'] * 4 / _rb['na']
for case in CASES:
    r = [x for x in res[case] if x['q'] == 'Q3 2027'][0]
    roe = r['nii'] * 4 / r['na']
    m_raw = a1 + b1 * roe
    m = min(m_raw, M_BASE) if case == 'bear' else max(m_raw, M_BASE) if case == 'bull' else m_raw
    if m != m_raw:
        print(f"  {case}: the line alone would give {m_raw:.2f}x on NII/NAV of {roe:.1%}; held at the base case's {M_BASE:.2f}x")
    tg[case] = m * r['nav_ps']
    VAL[case] = value(m, r['nav_ps'])
    detail[case] = (r['nav_ps'], roe, m)
    print(f"  {case}: NAV ${r['nav_ps']:.2f}; NII/NAV {roe:.1%}; on the line {m:.2f}x = ${tg[case]:.2f}; with {KEEP:.0%} of today's gap {m+KEEP*resid:.2f}x = ${VAL[case]:.2f}")
rbear = [x for x in res['bear'] if x['q'] == 'Q3 2027'][0]
print(f"  bear at today's {cion['pnav']:.2f}x NAV instead: ${cion['pnav']*rbear['nav_ps']:.2f}")
r = res['base'][3]
nav_adj = r['na'] - restate
roe_b = r['nii'] * 4 / r['na']; m_b = a1 + b1 * roe_b
x0 = np.array([1, roe_b]); se = (s2 * (1 + x0 @ XtXi @ x0)) ** 0.5
print(f"  how loose the line is: 80% prediction interval for the base case {m_b-T80*se:.2f}x to {m_b+T80*se:.2f}x = ${(m_b-T80*se)*r['nav_ps']:.2f} to ${(m_b+T80*se)*r['nav_ps']:.2f}")
lo_v, hi_v = value(m_b, r['nav_ps'], KEEP_HI), value(m_b, r['nav_ps'], KEEP_LO)
print(f"  base range from the 80% range of the persistence: ${lo_v:.2f} to ${hi_v:.2f}")
print("  base on other choices:")
print(f"    half on the line, half on today's gap: ${value(m_b, r['nav_ps'], 0.5):.2f} (my v20 draft also haircut PIK and got $6.18)")
print(f"    the line alone: ${tg['base']:.2f}")
roe_p = (r['nii'] - pik_q * (1 - PIKR['base'])) * 4 / r['na']
print(f"    PIK haircut to 79% on top of the carried gap (counts the market's PIK view twice): ${value(a1 + b1 * roe_p, r['nav_ps']):.2f}")
print(f"    all 18 peers in the line, same persistence: ${(a0 + b0 * roe_b + KEEP * (cion['pnav'] - (a0 + b0 * cion['roe']))) * r['nav_ps']:.2f}")
target = VAL['base']
dist12 = 0.10 + 10 * 0.25 / 3   # December 2026 declared, then ten months of the 2027 base
tr = (target + dist12) / px - 1
rating = 'BUY' if target > px * 1.15 else 'SELL' if target < px * 0.85 else 'HOLD'
print(f"TARGET: ${target:.2f} ({target/px-1:+.1%} vs ${px}); with ${dist12:.2f} of distributions a 12-month total return of {tr:+.1%}")
print(f"  on price: Buy above ${px*1.15:.2f}, Sell below ${px*0.85:.2f}; on total return the base case is {tr:+.1%}, also under the +15% Buy line")
print(f"RATING: {rating} (the 15% rule, on price and on total return, no override)")
print()
# reconciling with valuation.py's base write-down
import io as _io, contextlib as _cl
with _cl.redirect_stdout(_io.StringIO()):
    V = runpy.run_path(os.path.join(HERE, 'valuation.py'))
wd = I['net_assets_2026_09_30'] - V['vals'][1] * I['shares_outstanding_2026_09_30'] / 1000
losses = -CASES['base']['loss'] * 4
lvhit = lv * (1 - CASES['base']['lv'])
print(f"reconciliation: valuation.py's base writes NAV down {wd:,.0f}k. Through Sep 2027 this model takes {losses:,.0f}k of credit losses,")
print(f"  {lvhit:,.0f}k on Longview and no restatement, {losses+lvhit+restate:,.0f}k in all; the other {wd-losses-lvhit-restate:,.0f}k is")
print(f"  my bucket view, which values what's left at full rather than at a market multiple of about {detail['base'][2]:.2f}x")
print()
CR = {r['period']: r for r in rows('consensus_2026_11_13.csv')}
cons = {k: float(v['nii_per_share_consensus']) for k, v in CR.items()}
b = res['base']
fy27 = sum(x['nii_ps'] for x in b[1:])
fy26 = I['nii_per_share_9m_2026'] + b[0]['nii_ps']   # reported nine months plus my Q4
print("estimates, base case vs Seeking Alpha consensus (two analysts):")
for per, mine in (('Q4 2026', b[0]['nii_ps']), ('Q1 2027', b[1]['nii_ps']), ('Q2 2027', b[2]['nii_ps']), ('Q3 2027', b[3]['nii_ps']), ('Q4 2027', b[4]['nii_ps']), ('FY 2026', fy26), ('FY 2027', fy27)):
    rv = CR[per]
    extra = ''
    if rv['revision_3m_pct']:
        p3 = cons[per] / (1 + float(rv['revision_3m_pct']) / 100); p1 = cons[per] / (1 + float(rv['revision_1m_pct']) / 100)
        extra = f" (about ${p3:.2f} three months ago and ${p1:.2f} one month ago)"
    print(f"  {per} NII: mine ${mine:.2f}, consensus ${cons[per]:.2f}{extra}")
print(f"  NAV 31 Dec 2027: mine ${b[4]['nav_ps']:.2f} (bear ${res['bear'][4]['nav_ps']:.2f}, bull ${res['bull'][4]['nav_ps']:.2f}) vs ${I['nav_per_share_2026_09_30']:.2f} on 30 Sep 2026")
cov = [x['nii_ps'] / x['dist_ps'] for x in b[2:]]
print(f"  distribution coverage after the sale (base): {min(cov):.2f}x to {max(cov):.2f}x")
