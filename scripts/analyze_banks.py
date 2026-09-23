"""Descriptive public-balance-sheet scenarios; never an AI-adoption estimate."""
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from delegated_deposits.model import withdrawal_pmf
ROOT=Path(__file__).resolve().parents[1]
curves=pd.read_csv(ROOT/'results/curves.csv')
witnesses=json.loads((ROOT/'results/witnesses.json').read_text())

def envelope(h,liquidity):
    frame=curves[(curves.rho==.05)&(curves.h==h)].sort_values('cash')
    cash=np.clip(np.asarray(liquidity),0,1)
    # Convexity makes the chord between valid upper endpoints a valid upper.
    upper=np.interp(cash,frame.cash,frame.upper)
    j=np.minimum(np.floor(cash*200).astype(int),199)
    lower=np.zeros(len(cash))
    ws=witnesses[f'0.05_{h}']
    for index in np.unique(np.r_[j,j+1]):
        mask=(j==index)|(j+1==index)
        w=ws[index]
        support,prob=withdrawal_pmf(h,w['nodes'],w['masses'])
        values=np.maximum(support[None,:]-cash[mask,None],0)@prob
        lower[mask]=np.maximum(lower[mask],values)
    assert np.all(lower<=upper+1e-8)
    return lower,upper

def main():
    allrows=[];summaries=[];flow=[];descriptive=[]
    for date in ['20251231','20241231','20221231']:
        raw=json.loads((ROOT/f'data/raw/fdic_{date}.json').read_text())
        df=pd.DataFrame(r['data'] for r in raw['data'])
        flags=json.loads((ROOT/f'data/raw/fdic_insurance_{date}.json').read_text())
        flags=pd.DataFrame(r['data'] for r in flags['data'])
        assert not df.CERT.duplicated().any() and not flags.CERT.duplicated().any()
        df=df.merge(flags[['CERT','INSFDIC','INSDIF']],on='CERT',validate='one_to_one')
        counts={'date':date,'raw':len(df)}
        keep=(pd.to_numeric(df.INSFDIC)==1)&(df.BKCLASS!='OI')
        counts['not_insured_domestic_bank']=int((~keep).sum());df=df[keep].copy()
        valid=(df.DEPDOM>0)&(df.ASSET>0)&(df.CHBAL>=0)&df[['DEPDOM','ASSET','CHBAL']].notna().all(axis=1)
        counts['invalid_balance_sheet']=int((~valid).sum());df=df[valid].copy()
        counts['retained']=len(df);flow.append(counts)
        df['cash_ratio']=df.CHBAL/df.DEPDOM
        df['treasury_ratio']=(df.CHBAL+df.SCUST)/df.DEPDOM
        df['size_bin']=pd.cut(df.ASSET,[0,1e6,1e7,1e8,np.inf],labels=['<1bn','1-10bn','10-100bn','>=100bn'],right=False)
        df.to_csv(ROOT/f'data/processed/banks_{date}.csv',index=False)
        for label,frame in [('All',df)]+list(df.groupby('size_bin',observed=True)):
            descriptive.append({'date':date,'size':str(label),'banks':len(frame),
                                'deposits_trillion':frame.DEPDOM.sum()/1e9,
                                'assets_trillion':frame.ASSET.sum()/1e9,
                                'median_cash_ratio':frame.cash_ratio.median(),
                                'p10_cash_ratio':frame.cash_ratio.quantile(.1),
                                'p90_cash_ratio':frame.cash_ratio.quantile(.9),
                                'median_treasury_ratio':frame.treasury_ratio.median()})
        for theta in [.1,.25,.5]:
            for buffer in ['cash','cash_plus_treasury']:
                amounts=df.CHBAL if buffer=='cash' else df.CHBAL+df.SCUST
                delegated=theta*df.DEPDOM
                for h in [1.,.2,.05]:
                    lower,upper=envelope(h,amounts/delegated)
                    out=pd.DataFrame({'CERT':df.CERT,'date':date,'theta':theta,'buffer':buffer,'h':h,
                                      'lower_deposit_bps':lower*theta*10000,'upper_deposit_bps':upper*theta*10000,
                                      'lower_thousand_usd':lower*delegated,'upper_thousand_usd':upper*delegated})
                    allrows.append(out)
                    summaries.append({'date':date,'theta':theta,'buffer':buffer,'h':h,'banks':len(df),
                                      'median_lower_bps':np.median(lower)*theta*10000,
                                      'median_upper_bps':np.median(upper)*theta*10000,
                                      'sum_lower_billion':float(np.sum(lower*delegated)/1e6),
                                      'sum_upper_billion':float(np.sum(upper*delegated)/1e6),
                                      'weighted_upper_bps':float(np.sum(upper*delegated)/df.DEPDOM.sum()*10000),
                                      'max_interpolation_gap_bps':float(np.max(upper-lower)*theta*10000)})
    pd.concat(allrows).to_csv(ROOT/'results/bank_scenarios.csv.gz',index=False,
                            compression={'method':'gzip','mtime':0})
    pd.DataFrame(summaries).to_csv(ROOT/'results/bank_scenario_summary.csv',index=False)
    pd.DataFrame(descriptive).to_csv(ROOT/'results/bank_descriptive.csv',index=False)
    pd.DataFrame(flow).to_csv(ROOT/'results/sample_flow.csv',index=False)
    print(pd.DataFrame(flow).to_string(index=False))
    print(pd.DataFrame(summaries).query("date=='20251231' and theta==0.25").to_string(index=False))

if __name__=='__main__':main()
