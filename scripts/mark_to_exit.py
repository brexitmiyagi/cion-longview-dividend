# Mark-to-exit: when CION sells, gets repaid or restructures a position, how does what it
# realizes compare with where it had the position marked the quarter before?
#
# The 10-Q's Level 3 rollforward gives, for each quarter, net realized gains and losses, the
# total change in unrealized, and the change in unrealized on investments still held at the end
# of the quarter. The difference between the last two is the unrealized gain or loss reversed on
# the positions that left the book. Realized plus that reversal is what exits did to NAV against
# the prior quarter's marks: zero means the loss was already in the marks.
#
# One adjustment. When a loan bought at a discount is repaid early, the rest of the discount is
# booked as income (accretion), and the unrealized gain on it reverses. Q3 2025 had $19.4m of
# accretion against about $1.9m in a normal quarter. I treat accretion above the median quarter
# as part of what those exits realized. That's an estimate.
#
# Limits: Level 3 only (nearly all of CION's book); restructured loans come back as new
# securities that count as "still held"; Q4 2025 is missing because the 10-K only gives the year
# and "still held" can't be split by quarter. And it only sees what CION has exited. The loans
# still on the book, which is where the PIK sits, aren't tested by this.
import statistics as st
from common import inputs, rows

I = inputs()
sh = I['shares_outstanding_2026_09_30'] / 1000
R = rows('level3_rollforward.csv')
base_acc = st.median(float(r['accretion_of_discount_k']) for r in R)
print(f"median quarterly accretion {base_acc:,.0f}k, used as the normal level")
print("quarter  | realized | reversed on exits | extra accretion | exits vs prior marks | sales and repayments")
tot_real = tot_hit = tot_sales = 0.0
for r in R:
    real = float(r['net_realized_k']); rev = float(r['net_change_unrealized_k']) - float(r['unrealized_change_still_held_k'])
    extra = float(r['accretion_of_discount_k']) - base_acc
    hit = real + rev + extra; sales = float(r['sales_and_repayments_k'])
    tot_real += real; tot_hit += hit; tot_sales += sales
    print(f"  {r['quarter']}  {real:+9,.0f}k  {rev:+9,.0f}k  {extra:+8,.0f}k  {hit:+9,.0f}k  {sales:9,.0f}k")
print(f"six quarters: realized {tot_real:,.0f}k; exits did {tot_hit:,.0f}k to NAV against their prior-quarter marks"
      f" ({tot_hit/sh:+.2f}/share, {tot_hit/tot_real:.0%} of the realized loss was not in the marks a quarter earlier)")
print(f"  as a share of what left the book: exits at about {tot_sales/(tot_sales-tot_hit):.1%} of prior marks")
for b in (1500, 3000):
    h = sum(float(r['net_realized_k']) + float(r['net_change_unrealized_k']) - float(r['unrealized_change_still_held_k']) + float(r['accretion_of_discount_k']) - b for r in R)
    print(f"  sensitivity: normal accretion {b:,}k a quarter -> {h:,.0f}k")

# The same test on four other BDCs. Most of them only give the rollforward for nine months, so
# this compares nine-month figures, which measure exits against the marks at the start of the
# year rather than the quarter before. No accretion adjustment here, since I can't split normal
# from early-repayment accretion for the peers; CION's 2026 accretion was a normal level, its
# 2025 accretion was not, so I show 2025 for CION both ways.
print()
print("nine months, against the marks at the start of the year: share of realized losses that weren't in those marks")
for r in rows('peer_level3_9m.csv'):
    real = float(r['net_realized']); rev = float(r['net_change_unrealized']) - float(r['unrealized_change_still_held'])
    hit = real + rev; ex = float(r['exits'])
    share = max(0.0, hit / real) if real < 0 else 0.0
    line = f"  {r['lender']:5s} {r['period']}: realized {real:,.0f}, exits did {hit:+,.0f} to NAV ({hit/ex:+.1%} of exits), {share:.0%} of the realized loss was new"
    if r['lender'] == 'CION' and r['period'] == '9M 2025':
        adj = hit + float(r['accretion']) - 3 * base_acc
        line += f"; with the Q3 2025 accretion treated as exit proceeds {adj:+,.0f} ({adj/real:.0%})"
    print(line)

# Two gaps in the above: four peers is a small, hand-picked set, and Q4 2025 is missing. First,
# the full year 2025 from the 10-K, against the marks at the start of 2025:
F = {r['item']: float(r['value_k']) for r in rows('cion_level3_fy2025.csv')}
hit = F['net_realized'] + F['net_change_unrealized'] - F['unrealized_change_still_held']
adj = hit + F['accretion_of_discount'] - 4 * base_acc
print()
print(f"CION full year 2025 (10-K): realized {F['net_realized']:,.0f}k, exits did {hit:+,.0f}k to NAV ({hit/F['sales_and_principal_repayments']:+.1%} of exits), "
      f"{hit/F['net_realized']:.0%} of the realized loss was new; with accretion above four normal quarters treated as exit proceeds {adj:+,.0f}k "
      f"({adj/F['sales_and_principal_repayments']:+.1%}, {adj/F['net_realized']:.0%})")

# Second, every listed BDC with a calendar year whose Q3 2026 10-Q I could read cleanly
# (data/bdc_level3_9m_universe.csv, built by pull_bdc_level3.py from the XBRL, with a few totals
# taken from the 10-Q text where the tags were incomplete). The share measure only means something
# when there's a real realized loss, so it's ranked only where realized losses were at least 0.5%
# of exits. Restructurings distort it: when a loan is swapped for new securities, the old markdown
# can show up as "still held", which makes a loss look new. Blackstone Secured Lending's 2026 is
# mostly that (a $234m realized loss in Q3 alongside $191m of gains on positions still held).
print()
U = rows('bdc_level3_9m_universe.csv')
for per in ('9M 2026', '9M 2025'):
    out = []
    for r in U:
        if r['period'] != per: continue
        real = float(r['net_realized_m']); hit = real + float(r['net_change_unrealized_m']) - float(r['unrealized_change_still_held_m'])
        ex = float(r['exits_m'])
        share = hit / real if real < 0 and -real >= 0.005 * ex else None
        out.append((r['lender'], hit / ex, share))
    by_pct = sorted(out, key=lambda x: x[1])
    sh = sorted([x for x in out if x[2] is not None], key=lambda x: -x[2])
    print(f"{per}: {len(out)} listed BDCs. Exits against start-of-year marks, worst first:")
    print("   " + ", ".join(f"{n} {p:+.1%}" for n, p, _ in by_pct))
    print(f"   CION is {[n for n,_,_ in by_pct].index('CION')+1} of {len(by_pct)}; median {st.median(p for _,p,_ in out):+.1%}")
    print(f"   share of realized loss not in the marks ({len(sh)} with a real realized loss), highest first:")
    print("   " + ", ".join(f"{n} {s:.0%}" for n, _, s in sh))
    print(f"   CION is {[n for n,_,_ in sh].index('CION')+1} of {len(sh)}; median {st.median(s for _,_,s in sh):.0%}")

# The restructuring blind spot applies to CION's 2025 too. The 10-Q says 2025's realized losses came
# mainly from restructurings and write-offs, and the cash flow statement gives the non-cash
# restructurings. Blackstone's signature is a big realized loss with almost nothing reversed on
# exit. CION's main restructuring quarter (Q2 2025) shows most of the loss reversing an old markdown.
RS = {r['item']: float(r['value_k']) for r in rows('cion_restructurings_2025.csv')}
q2 = [r for r in R if r['quarter'] == 'Q2 2025'][0]
q2rev = float(q2['net_change_unrealized_k']) - float(q2['unrealized_change_still_held_k'])
print()
print(f"CION 2025 restructurings: {RS['restructuring_of_portfolio_investment_9m_2025']:,.0f}k of {float([r for r in rows('peer_level3_9m.csv') if r['lender']=='CION' and r['period']=='9M 2025'][0]['exits']):,.0f}k nine-month exits")
print(f"  Q2 2025 ({RS['restructuring_of_portfolio_investment_q2_2025']:,.0f}k restructured): realized {float(q2['net_realized_k']):,.0f}k, of which {q2rev:,.0f}k ({q2rev/-float(q2['net_realized_k']):.0%}) reversed markdowns already in the prior quarter's marks")
