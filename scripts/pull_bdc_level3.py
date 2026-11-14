# Rebuilds data/bdc_level3_9m_universe.csv from SEC. For every listed BDC with a calendar year it
# finds the 10-Q for 30 Sep 2026 and reads the Level 3 rollforward out of the inline XBRL: net
# realized, net change in unrealized, the change in unrealized on positions still held, and sales
# and repayments, for the nine months of 2026 and of 2025.
#
# BDCs tag this table in many different ways, so the parser is a best effort. Where a row label
# or a missing tag made it ambiguous I either took the total from the 10-Q text (TEXT below, every
# number checked by hand against the table) or left the BDC out. Put your own contact in UA.
# Needs network access; the rest of the repo doesn't.
import json, re, html, collections, csv, os, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'your name your@email'}
TICKERS = {'ARCC': 1287750, 'OBDC': 1655888, 'BXSL': 1736035, 'FSK': 1422183, 'MAIN': 1396440, 'TSLX': 1508655,
           'NMFC': 1496099, 'MFIC': 1278752, 'BBDC': 1379785, 'SLRC': 1418076, 'CGBD': 1544206, 'MSDL': 1782524,
           'CCAP': 1633336, 'TRIN': 1786108, 'TPVG': 1580345, 'OFS': 1487918, 'WHF': 1552198, 'CION': 1534254,
           'BCSF': 1655050, 'NCDL': 1737924}
# Parsed cleanly from XBRL (both periods unless noted)
CLEAN = ['OBDC', 'BXSL', 'FSK', 'MAIN', 'NMFC', 'MFIC', 'BBDC', 'CGBD', 'TPVG', 'WHF', 'CION', 'NCDL', 'BCSF', 'MSDL']
# $m, read from the 10-Q text where the tags were incomplete or carried the wrong sign
TEXT = {('ARCC', '9M 2026'): dict(held=-535), ('ARCC', '9M 2025'): dict(held=-57),
        ('TSLX', '9M 2026'): dict(held=-54.328), ('TSLX', '9M 2025'): dict(held=15.976),
        ('SLRC', '9M 2026'): dict(held=-18.695), ('SLRC', '9M 2025'): dict(held=4.724),
        ('CCAP', '9M 2026'): dict(held=-33.376), ('CCAP', '9M 2025'): dict(held=-5.768),
        ('MSDL', '9M 2026'): dict(real=-55.983, unreal=-80.606, held=-81.456),
        ('TRIN', '9M 2026'): dict(real=-18.166, unreal=-3.976, held=-20.837),
        ('OFS', '9M 2026'): dict(real=-24.001, unreal=5.004, held=-18.330, exit=84.008),
        ('OFS', '9M 2025'): dict(real=-10.414, unreal=-19.586, held=-26.348, exit=53.381)}
SKIP = {('MSDL', '9M 2026')}  # its XBRL realized total has the wrong sign; TEXT covers it
def parse(fn):
    t=open(fn,errors='ignore').read()
    ctx={}
    for m in re.finditer(r'<xbrli:context\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</xbrli:context>',t,re.S):
        cid,body=m.group(1),m.group(2)
        sd=re.search(r'<xbrli:startDate>([^<]+)',body); ed=re.search(r'<xbrli:endDate>([^<]+)',body); inst=re.search(r'<xbrli:instant>([^<]+)',body)
        dims=tuple(sorted((a,b.strip()) for a,b in re.findall(r'<xbrldi:explicitMember[^>]*dimension="([^"]+)"[^>]*>([^<]+)<',body)))
        typed=re.findall(r'<xbrldi:typedMember[^>]*dimension="([^"]+)"[^>]*>(.*?)</xbrldi:typedMember>',body,re.S)
        dims=dims+tuple((d,'typed:'+re.sub(r'<[^>]+>','',v).strip()) for d,v in typed)
        ctx[cid]=(sd.group(1) if sd else None,(ed or inst).group(1),dims)
    facts=[]
    for m in re.finditer(r'<ix:nonFraction\b([^>]*)>(.*?)</ix:nonFraction>',t,re.S):
        a=m.group(1); name=re.search(r'name="([^"]+)"',a).group(1); cr=re.search(r'contextRef="([^"]+)"',a).group(1)
        raw=re.sub(r'<[^>]+>','',m.group(2)).strip()
        if raw in ('','-','—'): v=0.0
        else:
            try: v=float(raw.replace(',',''))
            except: 
                v=None
        if v is None: continue
        sc=re.search(r'scale="(-?\d+)"',a); v*=10**int(sc.group(1)) if sc else 1
        if re.search(r'sign="-"',a): v=-v
        facts.append((name,cr,v))
    return ctx,facts

def row_labels(fn):
    """map ix fact id/position -> text label of its table row"""
    t=open(fn,errors='ignore').read()
    lab={}
    for tr in re.finditer(r'<tr\b.*?</tr>',t,re.S):
        row=tr.group(0)
        first=re.split(r'<ix:nonFraction',row,maxsplit=1)[0]
        txt=html.unescape(re.sub(r'<[^>]+>',' ',first)); txt=re.sub(r'\s+',' ',txt).strip()
        for m in re.finditer(r'<ix:nonFraction\b([^>]*)>',row):
            a=m.group(1); cr=re.search(r'contextRef="([^"]+)"',a).group(1); n=re.search(r'name="([^"]+)"',a).group(1)
            lab.setdefault((n,cr),txt)
    return lab

LOC=('StatementOfIncomeLocationBalanceAxis','IncomeStatementLocationAxis','StatementOfIncomeLocation')
def kind_concept(n):
    s=n.split(':')[1]
    if 'Unobservable' not in s and 'ChangeInUnrealizedGainLoss' not in s and 'StillHeld' not in s: return None
    if 'TextBlock' in s or 'Value' == s[-5:]: return None
    if re.search('Forward|Liabilit|Derivative|Currency|Swap|Option|Transfer|Purchase|Issuance|Affiliates|Hedg',s): return None
    if re.search('StillHeld|ChangeInUnrealizedGainLoss|HeldAtEnd|StillOwned',s): return 'held'
    if 'GainLoss' in s and 'Included' in s: return 'gl'
    if re.search('Unrealized',s): return 'unreal'
    if re.search('Realized',s): return 'real'
    if re.search('Sales|Settlement|Repayment|Disposition|Proceeds|Paydown|Redemption',s): return 'exit'
    if re.search('Accretion|Amortization',s): return 'acc'
    return None
def loc_kind(dims):
    for a,b in dims:
        if any(x in a for x in LOC):
            b=b.lower()
            if 'unrealized' in b or 'appreciation' in b: return 'unreal'
            if 'realized' in b: return 'real'
            return '?'
    return None
OK_AX=('FairValueByAssetClassAxis','InvestmentTypeAxis','FairValueByFairValueHierarchyLevelAxis','FinancialInstrumentAxis','InvestmentTypeCategorizationAxis','DebtSecuritiesAxis','FairValueByMeasurementBasisAxis')
def run(fn,sd,ed):
    ctx,facts=parse(fn)
    labs=row_labels(fn)
    groups=collections.defaultdict(dict)  # kind -> member -> value
    seen=set()
    for n,c,v in facts:
        k=kind_concept(n)
        if not k or c not in ctx: continue
        s,e,dims=ctx[c]
        if s!=sd or e!=ed: continue
        lk=loc_kind(dims)
        L0=labs.get((n,c),'').lower()
        if k=='held' and 'StillHeld' not in n and 'HeldAt' not in n and L0 and 'held' not in L0 and re.search('unrealized|appreciation|depreciation',L0):
            k='unreal'
        if k=='gl':
            if lk is None:
                L=labs.get((n,c),'').lower()
                if re.search('unrealized|appreciation|depreciation',L): lk='unreal'
                elif re.search('realized',L): lk='real'
            if lk in ('real','unreal'): k=lk
            else: k='gl?'
        other=[d for d in dims if not any(x in d[0] for x in LOC)]
        if any(not any(x in a for x in OK_AX) for a,b in other): continue
        lvl=[b for a,b in other if 'Hierarchy' in a]
        if lvl and not any('3' in x for x in lvl): continue
        mem=tuple(b for a,b in other if 'Hierarchy' not in a and 'MeasurementBasis' not in a) or ('TOTAL',)
        key=(k,n,mem)
        if key in seen: continue
        seen.add(key)
        groups[k][(n,mem)]=v
    if 'gl?' in groups:
        g=groups.pop('gl?')
        if 'real' not in groups and 'unreal' in groups: groups['real']=g
    out={}
    for k,g in groups.items():
        # collapse concepts: for exit, add different concepts (sales + settlements); others: one concept
        byc=collections.defaultdict(dict)
        for (n,mem),v in g.items(): byc[n][mem]=v
        tot=0.0
        for n,mm in byc.items():
            if ('TOTAL',) in mm: val=mm[('TOTAL',)]
            else:
                vals=list(mm.items()); val=None
                for mem,v in vals:
                    rest=sum(x for m2,x in vals if m2!=mem)
                    if len(vals)>2 and abs(v-rest)<=max(1.0,abs(v)*0.005) : val=v; break
                    if any(t in mem[-1] for t in ('InvestmentsMember','InvestmentOwnedMember','Total')) and len(mem)==1: val=v
                if val is None: val=sum(v for _,v in vals)
            if ('TOTAL',) in mm and len(mm)>1:
                rest=sum(v for m,v in mm.items() if m!=('TOTAL',))
                if abs(rest-mm[('TOTAL',)])>max(5e5,abs(mm[('TOTAL',)])*0.02): out.setdefault('flags',[]).append(f'{k}: members {rest/1e6:.1f}m vs total {mm[("TOTAL",)]/1e6:.1f}m')
            tot+=val if k=='exit' else 0
            if k!='exit': out.setdefault(k,val)
        if k=='exit': out[k]=abs(tot)
    return out

def get(u):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
        except Exception:
            time.sleep(2)
    raise RuntimeError(u)

def main():
    out = []
    for t, cik in TICKERS.items():
        s = json.loads(get(f'https://data.sec.gov/submissions/CIK{cik:010d}.json'))['filings']['recent']
        hit = next((a, p) for f, a, p, rd in zip(s['form'], s['accessionNumber'], s['primaryDocument'], s['reportDate']) if f == '10-Q' and rd == '2026-09-30')
        url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{hit[0].replace("-", "")}/{hit[1]}'
        fn = os.path.join(HERE, f'_{t}.htm'); open(fn, 'wb').write(get(url)); time.sleep(0.3)
        for per, (sd, ed) in {'9M 2026': ('2026-01-01', '2026-09-30'), '9M 2025': ('2025-01-01', '2025-09-30')}.items():
            o = run(fn, sd, ed)
            d = {k: (o[k] / 1e6 if isinstance(o.get(k), float) else None) for k in ('real', 'unreal', 'held', 'exit')}
            how = 'XBRL'
            if (t, per) in TEXT:
                d.update(TEXT[(t, per)]); how = '10-Q text' if t == 'OFS' else 'XBRL plus 10-Q text'
            elif t not in CLEAN or o.get('flags') or (t, per) in SKIP:
                continue
            if any(v is None for v in d.values()):
                continue
            out.append([t, per, round(d['real'], 3), round(d['unreal'], 3), round(d['held'], 3), round(d['exit'], 3), how, url])
        os.remove(fn)
    with open(os.path.join(HERE, '..', 'data', 'bdc_level3_9m_universe.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['lender', 'period', 'net_realized_m', 'net_change_unrealized_m', 'unrealized_change_still_held_m', 'exits_m', 'how', 'source'])
        w.writerows(out)
    print(len(out), 'rows')

if __name__ == '__main__':
    main()
