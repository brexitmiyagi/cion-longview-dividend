# Rebuilds data/bdc_panel.csv from SEC XBRL. You only need this if you want to refresh the
# data yourself. bdc_screen.py runs off the CSV that's already in data/.
#
# Steps: find every filer that tagged NetInvestmentIncome for a calendar year (frames API),
# pull each one's company facts, keep full years and nine-month periods, write one row per
# filer and period. SEC asks for a User-Agent with a contact, so put yours in below.
import os, csv, json, time, datetime as dt, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'bdc_panel.csv')
UA = {'User-Agent': 'your name your@email.com'}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=60))


ciks = {}
for y in (2022, 2023, 2024, 2025):
    for f in get(f'https://data.sec.gov/api/xbrl/frames/us-gaap/NetInvestmentIncome/USD/CY{y}.json')['data']:
        ciks[str(f['cik'])] = f['entityName']
    time.sleep(0.2)

tick = get('https://www.sec.gov/files/company_tickers.json')
first = {}
for v in tick.values():
    first.setdefault(str(v['cik_str']), v['ticker'])


def days(s, e):
    return (dt.date.fromisoformat(e) - dt.date.fromisoformat(s)).days


def series(facts, tag, kind):
    out = {}
    for u in facts.get('us-gaap', {}).get(tag, {}).get('units', {}).get('USD', []):
        s, e = u.get('start'), u['end']
        if kind == 'YE':
            if s is None and e[5:] == '12-31':
                k = e[:4]
            else:
                continue
        else:
            if not s:
                continue
            L = days(s, e)
            if kind == 'FY' and 330 <= L <= 380:
                k = e[:4]
            elif kind == '9M' and 255 <= L <= 285:
                k = e[:7]
            else:
                continue
        if k not in out or u['filed'] > out[k][1]:
            out[k] = (u['val'] if kind == 'YE' else abs(u['val']), u['filed'])
    return {k: v[0] for k, v in out.items()}


def first_of(facts, tags, kind):
    res = {}
    for t in tags:
        for k, v in series(facts, t, kind).items():
            res.setdefault(k, v)
    return res


w = csv.writer(open(OUT, 'w', newline=''))
w.writerow(['cik', 'name', 'ticker', 'period_kind', 'period', 'nii', 'total_investment_income', 'pik_income',
            'distributions_declared', 'drip_shares_issued', 'undistributed_ordinary_income_yearend'])
for cik, name in sorted(ciks.items()):
    try:
        f = get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json')['facts']
    except Exception:
        continue
    time.sleep(0.12)
    spill = series(f, 'InvestmentCompanyDistributableEarningsLossAccumulatedOrdinaryIncomeLoss', 'YE')
    for kind, keep in (('FY', ['2021', '2022', '2023', '2024', '2025']), ('9M', ['2024-09', '2025-09', '2026-09'])):
        nii = series(f, 'NetInvestmentIncome', kind)
        tii = series(f, 'GrossInvestmentIncomeOperating', kind)
        pa = series(f, 'InterestAndDividendIncomeOperatingPaidInKind', kind)
        pi = series(f, 'InterestIncomeOperatingPaidInKind', kind)
        pd = series(f, 'DividendIncomeOperatingPaidInKind', kind)
        pc = series(f, 'PaidInKindInterest', kind)
        dv = first_of(f, ['InvestmentCompanyDividendDistribution', 'DividendsCommonStock', 'DividendsCommonStockCash', 'Dividends'], kind)
        drip = series(f, 'StockIssuedDuringPeriodValueDividendReinvestmentPlan', kind)
        for p in keep:
            if p not in nii:
                continue
            pik = pa.get(p)
            if pik is None and (p in pi or p in pd):
                pik = pi.get(p, 0) + pd.get(p, 0)
            if p in pc:
                pik = max(pik or 0, pc[p])
            w.writerow([cik, name, first.get(cik, ''), kind, p, nii[p], tii.get(p, ''), '' if pik is None else pik,
                        dv.get(p, ''), drip.get(p, ''), spill.get(p, '') if kind == 'FY' else ''])
print('wrote', OUT)
