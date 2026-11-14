# CION's fee income since 2023, split by who paid it, and what the consensus needs.
# The statement of operations splits fee income (amendment, structuring, commitment and agent
# fees) by investment category. Non-affiliated is ordinary third-party borrowers. Affiliated
# (5% to 25% owned) and controlled (over 25%) are companies CION owns a stake in. The biggest single
# item: most of the $8.9m in Q3 2025 ($8.7m over nine months) came from JP Intermediate, restructured that year; the
# -$2.9m in Q3 2026 is STATinMED's fee reversed after its priming loan. data/fee_income_by_source.csv; Q4 is the 10-K year less nine months.
# Purchases of investments (cash flow statement, excludes PIK) are the new lending the fees come from.
import io, os, runpy, contextlib, statistics as st
from common import rows

HERE = os.path.dirname(os.path.abspath(__file__))
F = rows('fee_income_by_source.csv')
g = lambda r, k: float(r[k])
print("year | non-affiliated | owned companies | total | new lending | non-affiliated fees per $ of new lending")
for y in ('2023', '2024', '2025', '2026'):
    rs = [r for r in F if r['quarter'].startswith(y)]
    na = sum(g(r, 'fee_income_non_affiliated_k') for r in rs)
    ow = sum(g(r, 'fee_income_affiliated_k') + g(r, 'fee_income_controlled_k') for r in rs)
    p = sum(g(r, 'purchases_of_investments_k') for r in rs)
    lab = y if len(rs) == 4 else f"{y} (9M)"
    print(f"  {lab}: {na:,.0f}k | {ow:,.0f}k | {na+ow:,.0f}k | {p:,.0f}k | {na/p:.2%}")
base = [r for r in F if r['quarter'] < '2026']
na_q = st.mean(g(r, 'fee_income_non_affiliated_k') for r in base)
yld = sum(g(r, 'fee_income_non_affiliated_k') for r in base) / sum(g(r, 'purchases_of_investments_k') for r in base)
q3 = [r for r in F if r['quarter'] == '2026-Q3'][0]
h1 = [r for r in F if r['quarter'] in ('2026-Q1', '2026-Q2')]
h1_tot = st.mean(g(r, 'fee_income_non_affiliated_k') + g(r, 'fee_income_affiliated_k') + g(r, 'fee_income_controlled_k') for r in h1)
y25 = [r for r in F if r['quarter'].startswith('2025')]
tot25 = st.mean(g(r, 'fee_income_non_affiliated_k') + g(r, 'fee_income_affiliated_k') + g(r, 'fee_income_controlled_k') for r in y25)
pace = g(q3, 'purchases_of_investments_k')
print(f"2023-2025: non-affiliated fees {na_q:,.0f}k a quarter on average, {yld:.2%} of new lending")
print(f"Q3 2026 new lending {pace:,.0f}k; at the 2023-2025 fee rate that's {pace*yld:,.0f}k a quarter")

with contextlib.redirect_stdout(io.StringIO()):
    M = runpy.run_path(os.path.join(HERE, 'nav_model.py'))
run = M['run']; G = run.__globals__; core0 = G['core'] - G['B']['fee_base']   # take my base-case fee out, then put each case in
fy = lambda: sum(x['nii_ps'] for x in run('base')[1:])
cases = [('none (Q3 2026 ran at about zero)', 0.0),
         ('new lending at the Q3 2026 pace, 2023-2025 fee rate (my base case)', pace * yld),
         ('2023-2025 average, third-party borrowers only', na_q),
         ('first half 2026, all sources', h1_tot),
         ('2025 average, including fees from companies CION owns', tot25)]
print("fee income a quarter -> my 2027 NII:")
for lab, v in cases:
    G['core'] = core0 + v
    print(f"  {lab}: {v:,.0f}k -> ${fy():.2f}")
lo, hi = 0.0, 20000.0
for _ in range(50):
    m = (lo + hi) / 2; G['core'] = core0 + m
    lo, hi = (m, hi) if fy() < 1.13 else (lo, m)
G['core'] = core0 + G['B']['fee_base']
print(f"fee income needed for the $1.13 consensus: about {m:,.0f}k a quarter, {m/yld/1000:,.0f}m of new lending a quarter at the 2023-2025 fee rate")
