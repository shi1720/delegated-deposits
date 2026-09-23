"""Pre-specified central cases, refined after observing degree-512 gaps."""
from pathlib import Path
import sys,json
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from delegated_deposits.model import moment_bound,optimal_liquidity,beta_loss,common_state_floor
from delegated_deposits.certificate import exact_certificate,verify
ROOT=Path(__file__).resolve().parents[1]
rows=[];certs=[];banks=[]
for rho in [.01,.05,.2]:
    for h in [1.,.5,.2,.1,.05,.02]:
        for degree in [512,1024,2048,4096]:
            br=moment_bound(h,.3,.1,rho,degree,4001)
            rows.append(dict(h=h,mu=.1,rho=rho,cash=.3,degree=degree,lower=br.lower,
                             upper=br.upper,gap=br.gap,beta=beta_loss(h,.3,.1,rho),
                             floor=float(common_state_floor(.3,.1,rho))))
        cert=exact_certificate(h,.3,.1,rho,br);assert verify(cert);certs.append(cert)
        z=optimal_liquidity(h,.1,rho,.2,4096);z.pop('bound')
        banks.append(dict(h=h,mu=.1,rho=rho,ratio=.2,degree=4096,**z))
    print('refined',rho,flush=True)
pd.DataFrame(rows).to_csv(ROOT/'results/convergence.csv',index=False)
pd.DataFrame(banks).to_csv(ROOT/'results/bank_choice_refined.csv',index=False)
(ROOT/'results/rational_certificates_refined.json').write_text(json.dumps(certs,indent=2))
