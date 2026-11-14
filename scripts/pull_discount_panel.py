# Rebuilds data/bdc_discount_panel.csv: for CION and the 16 peers in my price-to-NAV line, each
# quarter-end from Q4 2023 to Q3 2026, net asset value per share, net assets and quarterly NII
# from SEC XBRL company facts, and the share price about six weeks after the quarter end (the
# first close on or after day 45, roughly when the quarter's NAV is public), from Yahoo.
# Needs network access. SEC asks for a User-Agent with a contact, so put yours in below.
import os, csv, json, time, datetime as dt, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'bdc_discount_panel.csv')
UA = {'User-Agent': 'your name your@email.com'}
TICKERS = ['CION', 'ARCC', 'BBDC', 'BCSF', 'BXSL', 'CGBD', 'FSK', 'HRZN', 'MFIC', 'MSDL', 'NCDL', 'OBDC', 'OFS',
           'OTF', 'PSBD', 'TCPC', 'TSLX']
QE = ['2023-12-31', '2024-03-31', '2024-06-30', '2024-09-30', '2024-12-31', '2025-03-31', '2025-06-30',
      '2025-09-30', '2025-12-31', '2026-03-31', '2026-06-30', '2026-09-30']

def get(url, ua=UA):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=60))

tick = get('https://www.sec.gov/files/company_tickers.json')
CIK = {v['ticker']: v['cik_str'] for v in tick.values()}

def facts(cik):
    return get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json')['facts']['us-gaap']

def instant(f, tag, unit, d):
    vals = [x for x in f.get(tag, {}).get('units', {}).get(unit, []) if x.get('end') == d and 'start' not in x]
    return vals[-1]['val'] if vals else None

def quarter_nii(f, d):
    # NetInvestmentIncome, or NII after tax where a filer doesn't tag that (FSK, NCDL in some
    # quarters); three-month value if tagged, otherwise year-to-date less the previous one
    for tag in ('NetInvestmentIncome', 'InvestmentIncomeOperatingAfterExpenseAndTax'):
        r = _quarter(f, tag, d)
        if r is not None:
            return r
    return None

def _quarter(f, tag, d):
    v = f.get(tag, {}).get('units', {}).get('USD', [])
    end = dt.date.fromisoformat(d)
    q = [x for x in v if x['end'] == d and 80 <= (end - dt.date.fromisoformat(x['start'])).days <= 100]
    if q:
        return q[-1]['val']
    ytd = [x for x in v if x['end'] == d and x['start'][:4] == d[:4] and x['start'][5:] == '01-01']
    if not ytd:
        return None
    y = ytd[-1]['val']
    if d[5:] == '03-31':
        return y
    prev = {'06-30': '03-31', '09-30': '06-30', '12-31': '09-30'}[d[5:]]
    pd_ = [x for x in v if x['end'] == d[:5] + prev and x['start'] == ytd[-1]['start']]
    return y - pd_[-1]['val'] if pd_ else None

def prices(t):
    j = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{t}?period1=1700000000&period2=1795000000&interval=1d',
            {'User-Agent': 'Mozilla/5.0'})['chart']['result'][0]
    return [(dt.datetime.fromtimestamp(s, dt.timezone.utc).date(), c) for s, c in zip(j['timestamp'], j['indicators']['quote'][0]['close']) if c]

with open(OUT, 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['ticker', 'quarter_end', 'nav_per_share', 'net_assets', 'nii_quarter', 'price_date', 'price', 'source'])
    for t in TICKERS:
        f = facts(CIK[t]); time.sleep(0.3)
        px = prices(t); time.sleep(0.3)
        for d in QE:
            nav = instant(f, 'NetAssetValuePerShare', 'USD/shares', d)
            na = instant(f, 'StockholdersEquity', 'USD', d) or instant(f, 'AssetsNet', 'USD', d)   # TSLX tags AssetsNet with the wrong sign
            nii = quarter_nii(f, d)
            target = dt.date.fromisoformat(d) + dt.timedelta(days=45)
            after = [x for x in px if x[0] >= target]
            if not after and px and (target - px[-1][0]).days <= 5:
                after = [px[-1]]   # the latest quarter: day 45 hasn't come yet, use the last close
            pdate, p = (after[0] if after else (None, None))
            w.writerow([t, d, nav, na, nii, pdate, round(p, 4) if p else None,
                        f'SEC XBRL company facts CIK {CIK[t]}; Yahoo Finance daily close'])
print('wrote', OUT)
