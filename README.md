# cion-longview-dividend

Data and code behind my Seeking Alpha piece on CION Investment Corporation (CION), "CION Investment: The 8.6% Notes Win On Risk, The Stock On Return" (November 2026).

The short version. Other SEC-registered funds own the same Longview units CION does and report their marks every quarter. CION bought 812,802 units in Q2 2024 for $12.00 each and marked them at $32.31 on June 30, 2024, the day an Eaton Vance-run portfolio marked the same units at $12.25 and a Virtus Seix fund at $11.88. On June 30, 2026 CION was at $72.74 and Virtus at $40.00. I also pulled net investment income, PIK income and distributions for every BDC that tags them in its SEC filings. Of the 37 that have filed nine-month results for 2025 and 2026, CION has the least NII left once PIK is taken out, 0.07x its distribution. In Q3 2026 a West Virginia coal plant, Longview Power, paid CION a $14.2 million dividend. CION paid its own shareholders $14.8 million. Take the plant out and Q3 net investment income was about $0.7 million. AEP agreed in July to buy the plant. This repo rebuilds that, checks CION's loan marks against other lenders and against what CION realized when it exited, models NII and NAV quarter by quarter through 2027, and values the stock and the listed notes.

## How to run

You need Python 3, nothing else. From anywhere:

    python3 scripts/tieout.py
    python3 scripts/longview_dividend.py
    python3 scripts/core_earnings_bridge.py
    python3 scripts/leverage_and_debt.py
    python3 scripts/market_implied.py
    python3 scripts/cash_coverage.py
    python3 scripts/longview_stake.py
    python3 scripts/book_quality.py
    python3 scripts/pearl_and_davids_bridal.py
    python3 scripts/capital_structure.py
    python3 scripts/valuation.py
    python3 scripts/bdc_screen.py
    python3 scripts/longview_cross_marks.py
    python3 scripts/plant_value.py
    python3 scripts/plant_dcf.py
    python3 scripts/peer_valuation.py
    python3 scripts/pik_cross_marks.py
    python3 scripts/mark_to_exit.py
    python3 scripts/distribution_cushion.py
    python3 scripts/nii_forecast.py
    python3 scripts/nii_bridge.py
    python3 scripts/rate_sensitivity.py
    python3 scripts/yield_context.py
    python3 scripts/fee_history.py
    python3 scripts/one_off_counts.py
    python3 scripts/buyback_math.py
    python3 scripts/dividend_cut_precedent.py
    python3 scripts/nav_model.py
    python3 scripts/notes_relative_value.py
    python3 scripts/incentive_fee_on_pik.py
    python3 scripts/fee_lookback.py
    python3 scripts/cross_mark_followup.py
    python3 scripts/interest_receivable.py
    python3 scripts/valuation_inputs.py
    python3 scripts/pik_marks.py
    python3 scripts/q3_to_run_rate.py
    python3 scripts/forward_rates.py
    python3 scripts/total_return.py
    python3 scripts/credit_metrics.py
    python3 scripts/realized_risk.py
    python3 scripts/discount_persistence.py
    python3 scripts/refinancing_2027.py

bdc_screen.py runs off data/bdc_panel.csv. If you want to rebuild that file from SEC yourself, put your own contact in the User-Agent line of pull_bdc_panel.py and run it. It takes a while because it pulls a few hundred company fact files.

My output from a clean run is in results/.

## What each script backs

- tieout.py checks the inputs against each other: Longview's Q3 dividend fits inside affiliated dividend income, the incentive fee recomputes to the reported $2.6 million, the debt table sums to $897 million, NAV per share is $13.20, the joint venture's loans sum to $176.9 million.
- longview_dividend.py gives Longview's dividends by quarter ($3.0m, $2.2m, $14.2m in 2026), the Q3 mark change, Q3 NII without the plant (1.5 cents a share), with the one-offs I can quantify added back (12.4 cents), and on management's count (19.5 cents). On the Q3 call management put three items at roughly $0.15 a share plus a $0.03 debt cost write-off. One of them, accrued income reversed on the Thrill One loan, isn't quantified anywhere, so I back it out as a residual (about $3.5 million). It's a credit cost, and my model charges credit losses separately, so I use management's count to avoid counting it twice.
- core_earnings_bridge.py rolls Q3 forward to a full quarter on the new balance sheet, starting from management's count of one-offs and adding fee income at Q3 2026's pace of new lending and CION's 2023-2025 fee rate (about $0.9 million a quarter): 21.4 cents a share before Longview, at flat rates. It also tests two uses of the Longview cash (about 26.5 cents with buybacks to 1.35x net leverage, about 24 cents if it all goes back into loans).
- q3_to_run_rate.py is the same walk in one column: Q3 2026 NII without Longview 1.5 cents, one-offs management named +10.9 to 12.4, the reorganized-loan reversal +7.1 to 19.5, the roll-forward +3.0 to 22.5, fee income +1.7 to 24.2, the incentive fee -2.8 to 21.4 cents. It also shows that this run-rate sits inside the fee's catch-up band ($10.6 million to $12.8 million of pre-incentive NII a quarter), so NII without Longview stays at 21.4 cents in Q4 and Q1 even with SOFR rising.
- forward_rates.py prints the SOFR futures curve of 13 Nov 2026 (data/sofr_futures_2026_11_13.csv: CME last trades, with Yahoo closes as a check) and every case on flat rates and on the curve (base 2027 NII $0.91 flat, $0.99 on the curve). It cross-checks the curve with fed funds futures (87bp of hikes by December 2027 against 89bp in SOFR futures) and Treasury bills (3 months 4.32%, 1 year 4.65%), from data/rates_crosscheck_2026_11_13.csv, and shows that measuring the shift from Q3 2026's average SOFR (3.67%) instead of the 10-Q's 3.88% would add about 2.4 cents a year, so the base is the cautious one.
- total_return.py compares 12-month total return for CION common and CICB in each case: bear -11.0% and +4.8%, base +12.3% and +8.6%, bull +38.1% and +9.5%; weighted 25/50/25, +13.0% and +7.9%. Against the realised volatility in realized_risk.py, CICB earns 0.47 over a one-year Treasury per unit of risk and the common 0.27 (this mixes forward returns with past volatility). CICB matches the common on expected return once the bear case gets 52%. A call of CICB at par on 30 Dec 2026 would pay $25.47 with the coupon, +4.1%. The CICB spread moves (+200bp bear, -50bp bull) are my assumption.
- credit_metrics.py gives non-accruals (4.85% at cost and 1.63% at fair value from the release; the schedule check ties to 1.63% at fair value), debt to equity (1.38x, 1.30x net), asset coverage (172% against the 150% floor, about $201 million of NAV room) and the maturity ladder ($327.5 million due in 2027).
- realized_risk.py measures what CION common and CICB have actually done since CICB listed (9 Oct 2024 to 13 Nov 2026, data/daily_prices_2024_2026.csv): total return -27.5% and +12.5%, volatility 30.5% and 6.8% a year, worst fall -40.1% (Mar 2025 to Jul 2026) and -3.9%. CICB rose 9.0% during the common's worst fall. Over the 2027 cut guidance (4 to 6 Nov 2026) the common fell 10.8%, CICB 0.6%, BIZD 1.0%.
- discount_persistence.py tests how much of a BDC's gap to the peer price-to-NAV line is still there a year later (data/bdc_discount_panel.csv, 96 peer pairs from Q2 2024 to Q3 2025 against four quarters later): 93%, 79% to 100% resampling by BDC. Of 17 cases at least 0.10x below the line, the gap narrowed in 9. The four-quarter windows overlap, so the pairs aren't independent. CION has been 0.16x to 0.27x below the line every quarter since mid-2024.
- pull_discount_panel.py rebuilds data/bdc_discount_panel.csv from SEC XBRL company facts and Yahoo prices. It needs network access and your own User-Agent.
- refinancing_2027.py sets the $327.5 million due in 2027 against cash and short-term investments ($51.0 million), the undrawn UBS facility ($25.0 million) and Longview cash left after buybacks in the base case ($24.1 million): about $227 million, 69%, left to refinance or pay from loan repayments, which ran about $121 million a quarter in 2026 without the joint-venture sale.
- leverage_and_debt.py gives reported net leverage (1.30x), leverage with the joint venture's notes and preferred added back (1.51x), the debt ranked by cost, and the $327.5 million due in 2027.
- market_implied.py gives price to NAV (0.46x) and what the market cap covers (Longview plus David's Bridal at their marks). It also gives the write-down the share price implies for the whole book: $349.8 million against the marks, $7.11 a share, against valuation.py's base write-down of $248.2 million (bear $569.9 million).
- cash_coverage.py gives CION's NII ex-PIK against distributions declared: 0.83x in 2023, 0.63x in 2024, 0.54x in 2025 and 0.07x in the first nine months of 2026 ($3.1 million against $44.8 million), minus $16.4 million without Longview. PIK was 92% of 2026 NII. It also prints a wider cash basis that takes out discount accretion too.
- longview_cross_marks.py lines up every other fund's per-unit Longview marks (data/longview_third_party_marks.csv, from their N-PORT and N-CSR filings) against CION's, gives the Q2 2024 purchase at $12.00 a unit and the $16.5 million day-one gain, and values CION's stake at the Virtus mark less the Q3 dividend ($30.50 a unit, $45.6 million, $1.09 a share below CION's mark).
- plant_dcf.py values Longview to retirement on its own heat rate, West Virginia coal prices (EIA-923) and EIA's November 2026 forecast for the PJM Western hub ($90.00 in 2027), with a location factor fitted to the market monitor's 2025 APS figure and tested on Jan-Sep 2026 (+7%). Base: $531 million, $748 per kW, 80% of CION's mark; it prints every sensitivity in the post, including the stake at 14% and 16%.
- peer_valuation.py compares 18 listed BDCs' price to NAV with NII ex-PIK coverage (R-squared 0.24) and PIK share (R-squared 0.01); median 0.73x.
- plant_value.py values the Longview plant from public data: EIA-923 output (4.63 million MWh in 2025, 74% capacity factor, 8,766 Btu/kWh), the PJM market monitor's APS-zone coal energy net revenue ($107,089 per MW in 2025, $180,821 in January to September 2026) and coal avoidable costs ($327.13 per MW-day), and 2026/27 capacity revenue. EBITDA is about $62 million a year on 2025 margins and $157 million on 2026 margins; at 5x that's $437 and $1,107 per kW. It also rebuilds January to September 2026 EBITDA (about $113 million) against what the owners paid out (about $130 million), converts each fund's mark into a value per kW, and shows the 2025 gap between CION's $ per kW input and its mark ($155 million in June 2025).
- bdc_screen.py is the sector screen: the 46-BDC constant panel for 2022 to 2025 (NII ex-PIK coverage 0.94x in 2023, 0.81x in 2025), the listed and non-traded splits, how much of each group's distributions went out as reinvested shares, undistributed income in months, and the 37-BDC ranking for the first nine months of 2026.
- pull_bdc_panel.py rebuilds data/bdc_panel.csv from SEC's XBRL frames and company facts APIs.
- longview_stake.py gives CION's Longview units, cost and mark per unit since 2023, the 2024 purchase at about $12.09 a unit, the implied value of the whole plant at a ~15% stake (~$662 million, ~$930 per kW) and the capacity revenue arithmetic from PJM's auction prices.
- book_quality.py sorts all 215 positions into buckets (cash-pay debt, PIK debt, no-cash PIK, non-accrual, equity, joint venture, Longview, David's Bridal) and gives the 50 cents the market implies for the riskier half.
- pearl_and_davids_bridal.py gives what the Pearl letter of intent would hand David's Bridal at different Pearl share prices and redemption levels.
- capital_structure.py gives asset coverage at book (172%) and at the share price (133%), and the yields on the CICB and CICC notes (8.63% and 8.35%).
- notes_relative_value.py also gives each note's spread over the matched-maturity Treasury (CICB 380bp, CICC 348bp, Great Elm's December 2029 notes 351bp, Oxford Square's 2030 notes 352bp), three months of trading volume, and what the 10-Q says about ratings (nothing for CICB or CICC).
- notes_relative_value.py sets CICB and CICC against 9 other listed BDC notes (13 Nov closes, maturities, call dates and each issuer's asset coverage from its latest 10-Q). Against the Great Elm and Oxford Square notes maturing 2029 to 2031, CICB yields 28bp more and CICC about the same.
- pik_cross_marks.py checks CION's loans against other lenders who hold the same ones (data/pik_cross_marks.csv, with each filing's URL). On the $130 million of shared loans, the other lenders' marks add up to $12.5 million less than CION's (25 cents a share, 9.6%). The seven largest PIK loans, $200 million, have no other public holder. It also works out the 79% base recovery for the PIK bucket that valuation.py uses.
- nii_forecast.py is the simpler four-quarter NII view (Longview sold at its mark, no credit losses, SOFR on the futures curve). Without any Longview dividend, Q4 2026 NII is about 21 cents; at the first-half average Longview payment it's about 25 cents; Longview would need to pay about $4.0 million for the 27 cent consensus, which it has done once.
- nii_bridge.py walks from my Q3 2027 NII (25.1 cents) to the consensus (29 cents) one assumption at a time: no credit losses (+1.6), Longview at its full mark (+2.2), fee income back to its first-half 2026 average (+4.3), 33.2 cents with all three. It prints the levels rounded and the steps as differences of the rounded levels, so the column adds up.
- rate_sensitivity.py shifts the whole SOFR futures curve in parallel and reruns the base case: 2027 NII of $0.89 at -100bp, $0.94 at -50bp, $0.99 on the curve, $1.04 at +50bp and $1.09 at +100bp, with Q3 2027 coverage of 0.90x to 1.11x. With SOFR flat at about 3.9%, as in my earlier drafts, 2027 is $0.91.
- fee_history.py splits CION's fee income since 2023 by who paid it (data/fee_income_by_source.csv, from each 10-Q and 10-K): third-party borrowers $7.9m, $9.9m, $9.4m and $5.0m (2023, 2024, 2025, 9M 2026); companies CION owns $3.8m, $8.0m, $10.6m and -$2.3m. Third-party fees ran at 2.52% of new lending over 2023-2025. On the futures curve it reruns 2027 under five fee levels ($0.92 with none, $0.99 at Q3's lending pace, $1.09 at the 2023-2025 third-party average, $1.13 at the first-half 2026 level, $1.29 at 2025's level including owned companies) and solves for what the $1.13 consensus needs: about $2.9 million a quarter, or $113 million of new lending a quarter at the usual fee rate. CION lent $34.7 million in Q3 2026 and no more than $81.8 million in any quarter since 2024.
- one_off_counts.py shows the two ways of counting the Q3 one-offs side by side: management's count (2027 NII $0.99, target $5.91) and my narrower one that leaves the Thrill One reversal in ($0.82, $5.13, which would be a Sell under my rule).
- buyback_math.py compares the base case with and without buybacks: buybacks add $0.50 a share to September 2027 NAV ($12.45 against $11.94).
- dividend_cut_precedent.py measures 14 regular BDC distribution cuts of 10% or more from 2024 to 2026, each matched to the press release that announced it (data/bdc_dividend_cuts.csv): the stock fell more than BIZD over the announcement in 13 of 14, by a median of 6.1%, and 6.4% where the yield before the cut was 13% or more. CION's November 2026 announcement of the 2027 cut cost 9.9% against BIZD.
- yield_context.py compares CION's yield on the 2027 base distribution (16.4% at $6.09) with listed peers' trailing yields (median 13.1%); CION ranks 5th of 19. At 20 cents a quarter it would yield about the peer median.
- nav_model.py is the main model. It runs NII and NAV quarter by quarter from Q4 2026 to Q4 2027 in three cases (credit losses at the 2026 pace, at the seven-quarter average, and at half the 2026 pace; Longview sold at 80%, 41% or 154% of CION's mark), with SOFR on the 13 Nov 2026 futures curve (common.curve_add; run(case, rate_add={}) gives flat rates). The peers' price-to-NAV line on NII return on NAV (16 listed BDCs, Hercules and Rand left out, R-squared 0.23) gives what CION would be worth at the peers' multiple; CION trades 0.21x below it. The target carries forward the share of that gap that discount_persistence.py finds still there after a year (93%). NII stays on the reported basis, PIK in full, because the gap is measured on that basis. Base: 2027 NII $0.99 against a $1.13 consensus, coverage 0.95x to 1.00x after the sale, NAV $12.45 in September 2027; on the line $8.29, target $5.91 (-3%), $5.73 to $6.27 across the persistence range; with 93 cents of distributions a 12.3% total return, a Hold on price and on total return. Bear $4.55, bull $7.48: both are held at the base case's multiple, because the line alone would pay the bear case more (its NAV falls faster than its NII); at today's 0.46x the bear case is $4.43. It also prints the line's 80% prediction interval ($5.84 to $10.74), half on the line ($7.01), all 18 peers ($5.89), a PIK haircut on top ($5.08, which counts the market's PIK view twice), how its losses reconcile with valuation.py (about $58 million through September 2027), and my quarterly estimates against the consensus.
- pearl_and_davids_bridal.py, with data/ferc_and_spac_facts.csv, also backs the David's Bridal section: K&F's November extension vote, the $239.8 million redeemed, and the new 6 August 2027 deadline.
- incentive_fee_on_pik.py rebuilds CION's income incentive fee every quarter from Q1 2024 to Q3 2026 (it ties to the reported fee within about $25,000 a quarter) and reruns it without PIK income. Of $48.4 million of fees, $32.7 million (67%) depended on PIK, and in 7 of the last 8 quarters the whole fee did. The number I lead with is smaller: at my 79% recovery, $6.1 million of fees (13%) were paid on PIK income I don't expect to be collected, about $2.2 million a year, 4.5 cents a share a year, 2.7% of NII over the period ($2.3 million at 90%, $9.9 million at 70%). The 10-K says the adviser doesn't have to pay any of it back. data/peer_advisory_terms.csv has the six peers I read first. data/fee_terms_20_bdcs.csv covers the 20 BDCs in the exit test, from each one's 2025 10-K: two are internally managed, and of the other 18 (CION included), eight cap the income fee by a trailing total return (Blackstone Secured Lending, MidCap Financial, Barings BDC, Morgan Stanley Direct Lending, TriplePoint, WhiteHorse, Bain Capital Specialty Finance, Nuveen Churchill). WhiteHorse also holds back the fee on PIK until the PIK is paid in cash. CION is one of the ten with neither. I found these by searching each 10-K for the cap and lookback language, so a BDC that words it differently could be misfiled; the detail column says what I found.
- fee_lookback.py applies the cap that Blackstone Secured Lending and Oaktree Specialty Lending have instead (17.5% of trailing twelve quarter pre-incentive NII less net capital losses, less fees already paid) to CION from Q4 2025, using data/fee_history_quarterly.csv. Under it CION's income fee would have been zero for all four quarters to September 2026, against $12.2 million paid, 24.9 cents a share.
- interest_receivable.py tracks interest receivable against quarterly income. It peaked at $49.4 million in September 2024 (0.83 of the quarter's income) and was $29.9 million (0.62) in September 2026. No sign of cash interest piling up unpaid.
- valuation_inputs.py compares the discount rates CION, FS KKR and OFS use on loans valued by discounted cash flow. CION's are higher (16.3% weighted against 11.3% and 12.35%), so its assumptions on rates don't explain why its marks run high.
- pik_marks.py goes borrower by borrower through nine quarters of CION's XBRL (data/cion_debt_by_borrower.csv, rebuilt by build_borrower_panel.py): which borrowers moved to PIK, how their marks moved, and which are held at par while PIK grows the loan. Trammell, P.C. has been at exactly 100% of principal for nine quarters while PIK took principal up 30%; Appalachian Resource, past its December 2025 maturity and paying only in PIK, went from 76% to 100% in Q2 2026.
- longview_cross_marks.py now includes a third outside holder, the City National Rochdale Fixed Income Opportunities Fund, whose marks match Virtus's to the cent every quarter.
- valuation.py is the cross-check: each bucket of the book at a share of its 30 September mark, bear $1.62, base $8.16, bull $13.02, weighted 35/45/20 to $6.84, or $5.81 if weighted by how the last seven quarters' credit losses actually ran. It lists what moving each bucket from base to bear costs: PIK loans $1.98 a share, David's Bridal $1.73, other equity $1.12, Longview $0.79. It also shows how well the assets left after the secured UBS facility cover the unsecured debt in each case (1.10x in the bear case, 1.50x base).
- mark_to_exit.py tests CION's marks against what it actually realized. From the Level 3 rollforward in six 10-Qs (Q1 2025 to Q3 2026, without Q4 2025), realized losses were $66.0 million and exits did $18.1 million to NAV against the prior quarter's marks (27%; $14.2 to $23.2 million depending on what counts as normal accretion). It runs the same test over nine months on FS KKR, Blue Owl Capital Corp, OFS and Barings BDC (data/peer_level3_9m.csv): in 2026, 69% of CION's realized losses weren't in its start-of-year marks, against 57% at FS KKR, 19% at Blue Owl, 3% at OFS and none at Barings. It also prints the second measure, what exits did to NAV as a share of the value exited: FS KKR is worse there (-7.9% against CION's -3.3%). I show both because each one flatters a different lender. The 2025 CION figure (81%) depends on how much accretion counts as normal, which the script also prints. Then it fills the two gaps: the full year 2025 from the 10-K (covers Q4; -9.0% of exits, -5.6% adjusted), and the same test on 20 listed BDCs with calendar years (data/bdc_level3_9m_universe.csv, built by pull_bdc_level3.py). In 2025 CION is worst of 18 on both measures; in 2026 it's 9th of 20 on loss per dollar exited and 6th of 18 on the share of losses that were new. Blackstone Secured Lending's bad 2026 is mostly one restructuring, which is the test's blind spot.
- mark_to_exit.py also checks the restructuring blind spot on CION's own 2025: $121.3 million of its $409.9 million nine-month exits were restructurings (data/cion_restructurings_2025.csv), but in its main restructuring quarter, Q2 2025, 65% of the realized loss reversed markdowns already taken the quarter before, which isn't the Blackstone pattern.
- cross_mark_followup.py asks whether the cross-mark gap predicts anything. For 35 borrowers CION shared with another listed BDC at September 2024 or 2025 (data/cross_mark_followup.csv), CION's mark a year later fell about 6 points where it had been more than 10 points above the others and about 10 points where it hadn't. No evidence the gap predicts markdowns, on a small and noisy sample.
- pull_bdc_level3.py rebuilds data/bdc_level3_9m_universe.csv from SEC. It needs network access and your own User-Agent. BDCs tag the Level 3 table many ways, so the parser is best effort; totals I took from the 10-Q text are listed in it.
- distribution_cushion.py gives CION's undistributed taxable income ($1.9 million at the end of 2025, under 4 cents a share) and what it paid out beyond NII in 2026 ($5.5 million). Its shortfall line uses flat rates; nav_model.py has the coverage on the futures curve.

## Sources

- EIA Short-Term Energy Outlook, November 2026 (Table 7a): https://www.eia.gov/outlooks/steo/
- EIA-860M, September 2026 generator inventory: https://www.eia.gov/electricity/data/eia860m/

- EIA-923 2025 final and 2026 monthly (plant 56671): https://www.eia.gov/electricity/data/eia923/
- Monitoring Analytics, 2025 State of the Market Report for PJM, Section 7: https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec7.pdf
- Monitoring Analytics, 2026 Q3 State of the Market Report for PJM: https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2026/2026q3-som-pjm.pdf
- PJM 2027/2028 auction release (17 Dec 2025): https://www.pjm.com/-/media/DotCom/about-pjm/newsroom/2025-releases/20251217-pjm-auction-procures-134479-mw-of-generation-resources.pdf
- Houlihan Lokey, Power, Utilities and Renewables Market Update, Year-End 2025: http://cdn.hl.com/pdf/2026/power-utilities-renewables-market-update-year-end-2025.pdf

- Virtus Seix Floating Rate High Income Fund N-PORT, 30 Jun 2026: https://www.sec.gov/Archives/edgar/data/1018593/000094040026035566/primary_doc.xml (every Virtus and Eaton Vance filing used is listed with its URL in data/longview_third_party_marks.csv)
- Brighthouse/Eaton Vance Floating Rate Portfolio N-CSRS, 30 Jun 2024: https://www.sec.gov/Archives/edgar/data/1126087/000119312524214978/d835978dncsrs.htm
- Eaton Vance Floating Rate Portfolio N-CSRS, 30 Apr 2024: https://www.sec.gov/Archives/edgar/data/1116914/000119312524169950/d832690dncsrs.htm
- CION 10-Q for Q2 2024: https://www.sec.gov/Archives/edgar/data/1534254/000153425424000017/cion-20240630.htm
- CION 10-Q for Q1 2024: https://www.sec.gov/Archives/edgar/data/1534254/000153425424000012/cion-20240331.htm

- SEC XBRL frames API (the BDC universe): https://data.sec.gov/api/xbrl/frames/us-gaap/NetInvestmentIncome/USD/CY2025.json
- SEC XBRL company facts API (each BDC's numbers): https://data.sec.gov/api/xbrl/companyfacts/CIK0001287750.json is ARCC's, swap in any CIK
- Ares Capital 10-Q for Q3 2026: https://www.sec.gov/Archives/edgar/data/1287750/000162828026067383/arcc-20260930.htm
- FS KKR 10-Q for Q3 2026: https://www.sec.gov/Archives/edgar/data/1422183/000162828026070499/fsk-20260930.htm
- FS KKR Q4 2025 earnings release: https://www.sec.gov/Archives/edgar/data/1422183/000110465926019719/tm267104d1_ex99-1.htm
- SOFR, daily (FRED, from the New York Fed): https://fred.stlouisfed.org/series/SOFR
- Three-month SOFR futures, last trades 13 Nov 2026: https://www.cmegroup.com/markets/interest-rates/stirs/three-month-sofr.quotes.html (Yahoo Finance SR3Z26.CME and the other contracts as a check)
- Fed funds futures (Yahoo Finance ZQZ26.CBT and later contracts) and Treasury bill yields (US Treasury daily par yield curve, 13 Nov 2026): data/rates_crosscheck_2026_11_13.csv
- Daily closes and ex-dates for CION, CICB and BIZD (Yahoo Finance, checked against Nasdaq historical quotes on the key dates): data/daily_prices_2024_2026.csv
- CION Q3 2026 earnings call (5 Nov 2026), transcript on Seeking Alpha: https://seekingalpha.com/article/4963279-cion-investment-corporation-cion-q3-2026-earnings-call-transcript
- CION 8-K, base distributions for Q1 2026 (7 Jan 2026): https://www.sec.gov/Archives/edgar/data/1534254/000110465926001616/tm262186d1_ex99-1.htm

- CION 10-Q for Q3 2026: https://www.sec.gov/Archives/edgar/data/1534254/000153425426000013/cion-20260930.htm
- CION 10-Q for Q2 2026: https://www.sec.gov/Archives/edgar/data/1534254/000153425426000010/cion-20260630.htm
- CION 10-Q for Q1 2026: https://www.sec.gov/Archives/edgar/data/1534254/000153425426000006/cion-20260331.htm
- CION 10-K for 2025: https://www.sec.gov/Archives/edgar/data/1534254/000153425426000003/cion-20251231.htm
- Other lenders' 10-Qs for 30 Sep 2026 used in the cross-marks: listed with URLs in data/pik_cross_marks.csv
- Peer advisory agreement terms (the 2025 10-K for each): listed with URLs in data/peer_advisory_terms.csv and data/fee_terms_20_bdcs.csv
- Listed notes: each issuer's latest 10-Q, listed with URLs in data/bdc_notes_2026_11_13.csv
- US Treasury daily par yield curve, 13 Nov 2026: https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026
- Analyst consensus: Seeking Alpha, CION earnings estimates and revisions pages, read 14 Nov 2026: https://seekingalpha.com/symbol/CION/earnings/estimates
- CION Q3 2026 earnings release: https://www.sec.gov/Archives/edgar/data/1534254/000110465926123088/tm2629026d1_ex99-1.htm
- CION 8-K on the joint venture and debt repayment (29 Sep 2026): https://www.sec.gov/Archives/edgar/data/1534254/000110465926111961/tm2626587d1_ex99-1.htm
- David's Bridal and Pearl letter of intent (22 Oct 2026): https://www.sec.gov/Archives/edgar/data/1534254/000110465926118023/tm2628044d1_ex99-1.htm
- AEP 10-Q for Q3 2026 (Longview purchase agreement): https://www.sec.gov/Archives/edgar/data/4904/000000490426000072/aep-20260930.htm
- PJM 2026/2027 capacity auction results: https://www.pjm.com/-/media/DotCom/about-pjm/newsroom/2025-releases/20250722-pjm-auction-procures-134311-mw-of-generation-resources-supply-responds-to-price-signal.pdf
- PJM 2028/2029 capacity auction results: https://www.pjm.com/-/media/DotCom/about-pjm/newsroom/2026-releases/20260714-pjm-capacity-auction-procures-138318-mw-of-generation-resources.pdf
- FERC eLibrary, docket EC26-153-000 (AEP/Longview): application 17 Aug 2026 (accession 20260817-5234), market monitor comments 16 Oct 2026 (20261016-5148), AEP response 30 Oct 2026 (20261030-5095)
- FERC eLibrary, docket EC25-59-000 (CION's 2024 Longview purchase): application 26 Feb 2025 (accession 20250226-5116)
- K&F Growth Acquisition Corp. II 8-K with the Pearl presentation (22 Oct 2026): https://www.sec.gov/Archives/edgar/data/2029976/000121390026111512/ea0309113-8k425_kfgrow2.htm
- K&F Growth Acquisition Corp. II 8-K on the extension vote (6 Nov 2026): https://www.sec.gov/Archives/edgar/data/2029976/000121390026116547/ea0311137-8k_kfgrow2.htm
- PJM 2026/2027 and 2028/2029 ELCC class ratings: https://www.pjm.com/-/media/planning/res-adeq/elcc/2026-27-bra-elcc-class-ratings.ashx and https://www.pjm.com/-/media/DotCom/planning/res-adeq/elcc/28-29-bra-elcc-class-ratings.pdf
- PJM 2025/2026 auction release (gives 2024/2025 at $28.92): https://www.pjm.com/-/media/DotCom/about-pjm/newsroom/2024-releases/20240730-pjm-capacity-auction-procures-sufficient-resources-to-meet-rto-reliability-requirement.pdf
- Longview Power 2020 Chapter 11 release: https://prnewswire.com/news-releases/longview-power-files-prepackaged-chapter-11-to-facilitate-ownership-change-301040002.html

## Things to be careful with

- The run-rate uses management's count of Q3 one-offs and assumes fee income at Q3 2026's lending pace and CION's 2023-2025 fee rate, about $0.9 million a quarter; fee_history.py shows what other fee levels do. Management said "roughly $0.15 per share" and didn't split it, so the Thrill One reversal (about $3.5 million) is a residual and could be off by a cent a share either way. My earlier, narrower count gave 15 cents a share for the run-rate quarter instead of 21; core_earnings_bridge.py prints both starting points.
- The consensus is two analysts and neither publishes assumptions. nii_bridge.py shows that fee income coming back closes the gap, but I can't confirm that's what they assume.
- The futures curve is a market forecast, not a promise. common.curve_add places each contract's rate at the middle of its reference quarter, ignores the one to three month lag before loans reset, and pushes the shift through the 10-Q's twelve-month rate table, which assumes a parallel move on the 30 September balance sheet. It's an approximation.
- AEP hasn't disclosed what it's paying for Longview. It isn't in AEP's Q3 10-Q, the FERC application keeps it in a confidential exhibit, news reports call it undisclosed, and an EDGAR full-text search turned up nothing else. I didn't search West Virginia Public Service Commission filings; AEP's buyer is its unregulated generation arm.
- The borrower panel adds up positions by a normalised borrower name, because CION renamed its positions twice. A few borrowers appear under two names in some quarters (Avison Young, the Hilliard firm), and Instant Web's June 2025 figure looks like a split I didn't capture, so I don't use it.

- The mark-to-exit test is an aggregate, not loan by loan, because the 10-Q doesn't give proceeds by loan. Restructured loans come back as new securities and count as still held (Blackstone Secured Lending's 2026 is the clearest case), Q4 2025 can't be split out of the 10-K on its own so I use the full year instead, and early repayments of discounted loans move income and unrealized at the same time, which I handle with an estimate of normal accretion. It also only sees what CION exited, not the loans still on the book.
- nav_model.py holds the rest of the book flat apart from the credit losses I assume, keeps the distribution at 25 cents, and assumes AEP closes at the end of Q1 2027. The peer line has an R-squared of 0.23, and the persistence test covers only two years and 16 BDCs. Both are printed with their ranges.
- The 20-BDC exit test only covers BDCs whose September 10-Q I could read cleanly. Calendar-year filers only, so Golub, Oaktree, PennantPark and a few others with September year-ends are out, and some calendar-year BDCs tag the table in ways I couldn't parse reliably (Hercules, Prospect, Goldman Sachs BDC, Capital Southwest, BlackRock TCP and others). Exits aren't defined the same way everywhere: some include distributions from structured holdings, some include restructurings.
- cross_mark_followup.py matches borrowers by company name, not tranche, so some pairs compare different loans. Isagenix and Avison Young look like that. It's 35 pairs over two years, which is small.
- The quarterly credit losses can't split Longview's mark out of Q1 and Q2 2025 separately, only for the half year.

- The PIK cross-marks only cover loans someone else also holds and reports. That's a quarter of the PIK bucket. The biggest PIK loans (Instant Web, Homer City, EagleTree, the two law-firm loans, Appalachian Resource, Berlitz) have no outside mark, so for those I'm still using my own 75%. Where two other lenders hold a loan I use the average of their marks; where the tranche isn't identical (Main Street's RA Outdoors piece is a 2028 tranche) I say so in the file.
- The consensus is two analysts, read off Seeking Alpha on 14 November. I don't know whether they count Longview dividends. The prior-period figures are worked back from Seeking Alpha's revision percentages.
- The notes trade flat. Yahoo shows ex-interest dates for CICB like a stock's ex-dividend dates, so I treat the close as the full price. If you treat it as a clean price and add accrued interest, the yields come out lower.
- The NII forecast holds the rest of the book flat for a year. No new defaults, no growth, no fee income unless I say so.

- Longview's quarterly dividend is a difference of two year-to-date columns from two different 10-Qs. The Q3 figure ($14.2 million) sits inside the $14.3 million of affiliated dividend income on the income statement, which is the check I lean on.
- The Q4 bridge is mine. The day counts come from the repayment and sale dates, but the joint venture's distributions, the preferred return (not disclosed, I use 10%) and the timing of the other repayments are estimates.
- I assume CION gets roughly its September 30 mark for Longview. AEP hasn't disclosed the price.
- The look-through leverage adds back debt CION isn't legally on the hook for. It's an economic view.
- The bucket recoveries in valuation.py are judgment calls. Change them and see what moves.
- The ~15% Longview stake is "approximately 15 percent" in the 2025 FERC filing. The implied plant value moves with it.
- The cash-basis NII ignores working capital and treats all PIK as unpaid. Some PIK gets collected on repayment.
- The capacity revenue lines are back-of-envelope: 710 MW times PJM's coal accreditation times the auction price, before outages, penalties or bonuses. For years without a published coal rating I use 83%.
- I parsed the schedule of investments from the 10-Q text. tieout.py checks the buckets sum to the $1,471.3 million portfolio.
- The share price is the 13 November 2026 close ($6.09), the day CION went ex a $0.10 distribution. It will move.
- The Longview cross-marks assume the units are comparable. CION and, in early 2024, Eaton Vance call them Longview Intermediate Holdings C LLC. Virtus calls its holding Longview Intermediate Holdings LLC, the name Eaton Vance used before and after. If the classes differ, the comparison with Virtus weakens. The Eaton Vance comparison doesn't depend on it.
- Eaton Vance's Floating Rate Portfolio and Senior Debt Portfolio feed other Eaton Vance funds, so the same units show up in more than one filing. I list each filing as it is and don't add them up.
- Virtus's own Virtus Asset Trust schedules (in thousands of dollars) match its N-PORT values, which is the second check on those numbers.
- AEP hasn't disclosed the price, so nothing here says which mark is right. The sale will.
- plant_dcf.py's power path after 2027, the $250 capacity price after May 2029, the 2040 retirement, the 80% capacity factor and the 10% discount rate are my assumptions; the script prints what each one does. The location factor is fitted to a zonal figure, not Longview's own node.
- Peer prices are 13 Nov 2026 closes and NAVs are 30 Sep 2026; CION's coverage is below every peer, so the fitted line extrapolates.
- plant_value.py uses the market monitor's model coal plant, not Longview's own costs, which EIA redacts. Longview's heat rate is better than the model's. The 4x to 6x multiples are mine; the gas deals in data/thermal_comps.csv traded at 7.0x to 7.9x. The 2025/26 coal accreditation is a stand-in (83%), as is 2027/28. Case B annualizes January to September 2026 by four-thirds.
- The 2020 exit term loan rows in data/longview_term_loan.csv show it halved in Q3 2022 and gone from every holder's filing by early 2023, so debt doesn't explain CION's 2025 marks.
- CION's own level 3 table gives a $ per kW input for the line that matches Longview's fair value each quarter: $442.50 (Sep 2024), $450 (Dec 2024), $440 (Jun 2025), $817.50 (Sep 2025), $1,000 (Dec 2025 and Mar 2026), $1,025 (Jun 2026), $938 (Sep 2026). These are in data/cion_longview_valuation_input.csv, transcribed from the 10-Qs and 10-Ks listed there.
- Eaton Vance's two largest portfolios marked the units at $2.75 on 30 Apr 2024 and then sold at $12.00. Outside marks on this asset are noisy, which is why the post leans on the $12.00 trade and on the outside funds moving to it, not on any one fund's level.
- The sector screen uses the XBRL tags as filed. Most filers tag NII before excise and income tax, so it's a little above the NII in their releases, which flatters coverage slightly. Not every BDC tags PIK, so the panel is the BDCs that do. I drop rows where NII is under half or over 2.5x distributions for the same period, because those are almost always a quarter tagged as a year or a missing tag, and the script prints every row it drops. Two filers that use BDC tags but aren't BDCs are excluded by name.
- Distributions include specials paid out of earlier years' income. A BDC can run below 1x for a while without anything being wrong.
- For CION's own numbers I use after-tax NII and PIK capitalized from the cash flow statement, both from the filings, so CION's lines in cash_coverage.py and bdc_screen.py differ in the second decimal.

## Corrections

None so far.

## Changes

- 14 Nov 2026: the base case now follows the SOFR futures curve instead of holding SOFR flat (2027 NII $0.99, was $0.91), and the target weights the peer line and today's discount to it equally instead of using the line alone (target $6.18, was $7.10). The earlier numbers are still printed: forward_rates.py for flat rates, nav_model.py with 100% weight on the line.
- 14 Nov 2026 (later): the target now carries forward the 93% of the gap to the peer line that discount_persistence.py finds peers still carry a year later, with NII on the reported basis, instead of a 50/50 judgment weight with a PIK haircut. Target $5.91 (was $6.18). The risk comparison between the common and CICB now uses realised volatility (realized_risk.py) instead of the spread across my scenarios.
- 14 Nov 2026 (v22): bear and bull cases held at the base case's price-to-NAV multiple (bear $4.55, was $4.77; bull $7.48, was $7.36). Target unchanged at $5.91.
