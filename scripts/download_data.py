"""Download unmodified public FDIC responses with provenance and hashes."""
import hashlib,json,time,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'
FIELDS='CERT,NAME,REPDTE,ASSET,DEP,DEPDOM,DEPINS,DEPUNINS,CHBAL,SC,SCUST,LNLSNET,BRO,SCMTGBK,BKCLASS'

def save(url,path):
    if path.exists() and path.with_suffix(path.suffix+'.meta.json').exists():return
    for trial in range(4):
        try:
            with urlopen(url,timeout=90) as response:payload=response.read()
            path.write_bytes(payload)
            meta={'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),
                  'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
            path.with_suffix(path.suffix+'.meta.json').write_text(json.dumps(meta,indent=2)+'\n')
            return
        except Exception:
            if trial==3:raise
            time.sleep(2*(trial+1))

def main():
    RAW.mkdir(parents=True,exist_ok=True)
    save('https://api.fdic.gov/banks/docs/risview_properties.yaml',RAW/'fdic_fields.yaml')
    for date in ['20251231','20241231','20221231']:
        url='https://api.fdic.gov/banks/financials?'+urlencode({
            'filters':f'REPDTE:{date}','fields':FIELDS,'limit':10000,
            'sort_by':'CERT','sort_order':'ASC','format':'json'})
        path=RAW/f'fdic_{date}.json';save(url,path)
        data=json.loads(path.read_text())
        assert len(data['data'])==data['meta']['total'],'Incomplete API download'
        flag_url='https://api.fdic.gov/banks/financials?'+urlencode({
            'filters':f'REPDTE:{date}','fields':'CERT,REPDTE,INSFDIC,INSDIF,BKCLASS',
            'limit':10000,'sort_by':'CERT','sort_order':'ASC','format':'json'})
        save(flag_url,RAW/f'fdic_insurance_{date}.json')
        print(date,len(data['data']),flush=True)

if __name__=='__main__':main()
