# Rebuilds data/cion_debt_by_borrower.csv from CION's XBRL filings: every debt position's fair
# value, cost, principal and PIK rate, added up by borrower, for each quarter from Q3 2024 to
# Q3 2026. CION changed how it names positions twice in that time, so borrower names are
# normalised (co() below) before adding up. Download the *_htm.xml instance from each 10-Q/10-K
# into xbrl/ next to this script, named by quarter end (e.g. xbrl/2026-09-30.xml), then run it.
import re,glob,json,collections,sys,os,csv
HERE = os.path.dirname(os.path.abspath(__file__))
T=['Senior Secured First Lien Debt','Senior Secured Second Lien Debt','Collateralized Securities and Structured Products - Equity','Collateralized Securities and Structured Products - Debt','Unsecured Debt','Equity','Short Term Investments']
def kind(k):
    for t in T:
        if t in k: return t
    return '?'
def co(k):
    if ' | ' in k:
        parts=[p.strip() for p in k.split(' | ') if p.strip() not in T and 'Maturity' not in p]
        n=parts[0] if parts else k
    else:
        n=k
        for t in sorted(T,key=len,reverse=True):
            i=n.find(', '+t)
            if i>0: n=n[:i]; break
    n=re.sub(r'[,\s]+\d+$','',n.strip())
    n=re.sub(r'(?i),\s*(Class|Series|Common|Preferred|Membership|Warrant|Units|LLC Interests|Common LLC|Escrow|Trust|Senior Preferred|Participating|Contingent|Ordinary|Rights|Subordinated).*$','',n)
    n=re.sub(r'\(.*?\)','',n)
    n=re.sub(r'(?i)[,.&]|amp;|\b(inc|llc|l\.?l\.?p|lp|p\.?c|corp|corporation|holdings?|holdco|company|co|ltd|limited|group|the|parent|intermediate|acquisition|acquisitionco|buyer|borrower|opco|topco)\b','',n)
    n=re.sub(r'\d+/\d+/\d+ maturity','',n.lower())
    return ' '.join(n.split())[:24]
out={}
for f in sorted(glob.glob(os.path.join(HERE, 'xbrl', '*.xml'))):
    d=f.split('/')[-1][:-4]; x=open(f).read()
    ctx={}
    for m in re.finditer(r'<context id="([^"]+)">(.*?)</context>',x,re.S):
        body=m.group(2)
        t=re.search(r'InvestmentIdentifierAxis">\s*<[^>]+>(.*?)</',body,re.S)
        inst=re.search(r'<instant>([^<]+)</instant>',body); dur=re.search(r'<endDate>([^<]+)</endDate>',body)
        if t and 'explicitMember' not in body and ((inst and inst.group(1)==d) or (dur and dur.group(1)==d) or (not inst and not dur)):
            ctx[m.group(1)]=t.group(1).strip()
        elif t and 'explicitMember' not in body and inst is None:
            ctx[m.group(1)]=t.group(1).strip()
    pos=collections.defaultdict(dict)
    for tag,key in (('InvestmentOwnedAtFairValue','fv'),('InvestmentOwnedAtCost','cost'),('InvestmentOwnedBalancePrincipalAmount','par'),('InvestmentInterestRatePaidInKind','pik')):
        for m in re.finditer(r'<us-gaap:%s\s+contextRef="([^"]+)"[^>]*>([^<]+)<'%tag,x):
            if m.group(1) in ctx:
                try: pos[ctx[m.group(1)]][key]=float(m.group(2))/(1000 if key!='pik' else 1)
                except ValueError: pass
    agg=collections.defaultdict(lambda:{'cost':0.0,'fv':0.0,'par':0.0,'pik':0.0,'n':0})
    pikco=collections.defaultdict(float)
    for k,v in pos.items():
        if v.get('pik',0)>0: pikco[co(k)]=max(pikco[co(k)],v['pik'])
    for k,v in pos.items():
        if 'cost' not in v or 'Short Term' in k or kind(k) in ('Equity','?') or 'Collateralized' in kind(k): continue
        a=agg[co(k)]; a['cost']+=v['cost']; a['fv']+=v.get('fv',0); a['par']+=v.get('par',0); a['pik']=max(a['pik'],v.get('pik',0)); a['n']+=1
    for c in agg: agg[c]['pik']=max(agg[c]['pik'],pikco.get(c,0))
    out[d]=agg
    print(d,len(agg),'with PIK',sum(1 for a in agg.values() if a['pik']>0),'debt fv',round(sum(a['fv'] for a in agg.values())),'PIK fv',round(sum(a['fv'] for a in agg.values() if a['pik']>0)))
with open(os.path.join(HERE, '..', 'data', 'cion_debt_by_borrower.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['quarter_end','borrower_key','principal_k','cost_k','fair_value_k','max_pik_rate','positions'])
    for d in sorted(out):
        for c,a in sorted(out[d].items()):
            w.writerow([d,c,round(a['par']),round(a['cost']),round(a['fv']),round(a['pik'],4),a['n']])
