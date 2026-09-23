from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'paper'

def write(name,rows):
    (P/name).write_text('\n'.join(' & '.join(map(str,row))+r' \\' for row in rows)+'\n')

def main():
    s=pd.read_csv(ROOT/'results/moment_sweep.csv');r=pd.read_csv(ROOT/'results/convergence.csv')
    rows=[]
    for h in [1,.5,.2,.1,.05,.02]:
        independent=s[(s.mu==.1)&(s.rho==0)&(s.cash==.3)&(s.h==h)].iloc[0]
        x=r[(r.rho==.05)&(r.degree==4096)&(r.h==h)].iloc[0]
        rows.append([f'{h:.0%}'.replace('%',r'\%'),f'{100*independent.lower:.5f}',f'{100*x.beta:.5f}',
                     f'{100*x.lower:.5f}',f'{100*x.upper:.5f}',f'{10000*x.gap:.3f}'])
    write('table-risk.tex',rows)
    d=pd.read_csv(ROOT/'results/bank_descriptive.csv');rows=[]
    labels={'All':'All banks','<1bn':r'Below \$1bn','1-10bn':r'\$1--10bn','10-100bn':r'\$10--100bn','>=100bn':r'\$100bn or more'}
    for _,x in d[d.date==20251231].iterrows():
        rows.append([labels[x['size']],f'{x.banks:,}',f'{x.deposits_trillion:.3f}',
                     f'{100*x.median_cash_ratio:.2f}',f'{100*x.p10_cash_ratio:.2f}',f'{100*x.p90_cash_ratio:.2f}'])
    write('table-data.tex',rows)
    b=pd.read_csv(ROOT/'results/bank_scenario_summary.csv');rows=[]
    for _,x in b[(b.date==20251231)&(b.buffer=='cash')].iterrows():
        rows.append([f'{100*x.theta:.0f}',f'{100*x.h:.0f}',f'{x.median_lower_bps:.2f}--{x.median_upper_bps:.2f}',
                     f'{x.weighted_upper_bps:.2f}',f'{x.max_interpolation_gap_bps:.2f}'])
    write('table-scenarios.tex',rows)
    f=pd.read_csv(ROOT/'results/assumption_sensitivity.csv');rows=[]
    for _,x in f.iterrows():
        rx=r[(r.rho==.05)&(r.degree==4096)&(r.h==x.h)].iloc[0]
        rows.append([f'{100*x.h:.0f}',f'{100*rx.lower:.5f}--{100*rx.upper:.5f}',f'{100*x.finite_exchangeable:.5f}'])
    write('table-assumptions.tex',rows)
    flow=pd.read_csv(ROOT/'results/sample_flow.csv');rows=[]
    for _,x in flow.iterrows():
        rows.append([str(int(x.date)),f'{x.raw:,}',str(x.not_insured_domestic_bank),str(x.invalid_balance_sheet),f'{x.retained:,}'])
    write('table-flow.tex',rows)
    rows=[]
    for _,x in b[(b.theta==.25)&(b.h==.05)].iterrows():
        rows.append([str(int(x.date)), 'Cash' if x.buffer=='cash' else 'Cash + Treasuries',
                     f'{x.banks:,}',f'{x.median_lower_bps:.2f}--{x.median_upper_bps:.2f}'])
    write('table-dates.tex',rows)
    print(d[d.date==20251231].to_string(index=False))

if __name__=='__main__':main()
