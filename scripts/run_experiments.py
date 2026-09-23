import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys,json,hashlib,time
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.stats import binom
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from delegated_deposits.model import *
from delegated_deposits.certificate import exact_certificate,verify
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
CAPS=[1.,.5,.2,.1,.05,.02]

def main():
    started=time.time()
    protocol=ROOT/'notes/protocol.md'
    (OUT/'protocol_hash.json').write_text(json.dumps({'sha256':hashlib.sha256(protocol.read_bytes()).hexdigest()},indent=2))
    rows=[]
    for mu in [.05,.1,.2]:
        for rho in [0.,.01,.05,.2,1.]:
            for h in CAPS:
                for cash in [.1,.2,.3]:
                    br=moment_bound(h,cash,mu,rho,512)
                    rows.append(dict(mu=mu,rho=rho,h=h,cash=cash,lower=br.lower,upper=br.upper,
                                     gap=br.gap,beta=beta_loss(h,cash,mu,rho),
                                     floor=float(common_state_floor(cash,mu,rho)),moment_residual=br.moment_residual))
        print('fixed-cash sweep',mu,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'moment_sweep.csv',index=False)
    rows=[]
    for rho in [0.,.01,.05,.2,1.]:
        for ratio in [.05,.2,.5]:
            for h in CAPS:
                z=optimal_liquidity(h,.1,rho,ratio,512)
                z.pop('bound')
                rows.append(dict(mu=.1,rho=rho,h=h,ratio=ratio,**z))
        print('bank choice',rho,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'bank_choice.csv',index=False)
    # Dense fixed-cash curves also supply bankwise interpolation envelopes.
    rows=[];witnesses={}
    for rho in [0.,.05,.2]:
        for h in CAPS:
            ws=[]
            for cash in np.linspace(0,1,201):
                br=moment_bound(h,float(cash),.1,rho,512)
                rows.append(dict(mu=.1,rho=rho,h=h,cash=cash,lower=br.lower,upper=br.upper,
                                 beta=beta_loss(h,float(cash),.1,rho)))
                ws.append({'cash':float(cash),'nodes':br.nodes.tolist(),'masses':br.masses.tolist()})
            witnesses[f'{rho}_{h}']=ws
        print('curves',rho,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'curves.csv',index=False)
    (OUT/'witnesses.json').write_text(json.dumps(witnesses))
    # Exact-arithmetic audit for central, fixed-cash cases.
    certs=[]
    for rho in [.01,.05,.2]:
        for h in CAPS:
            br=moment_bound(h,.3,.1,rho,512)
            cert=exact_certificate(h,.3,.1,rho,br);assert verify(cert);certs.append(cert)
    (OUT/'rational_certificates.json').write_text(json.dumps(certs,indent=2))
    # Independent simulation uses directly sampled conditional binomials.
    rng=np.random.default_rng(1720406);rows=[];N=1_000_000
    for h in [.2,.05,.02]:
        br=moment_bound(h,.3,.1,.05,512)
        for label,nodes,masses in [('worst-grid',br.nodes,br.masses),('independent',np.array([.1]),np.array([1.]))]:
            p=rng.choice(nodes,size=N,p=masses/masses.sum())
            W=rng.binomial(round(1/h),p)*h
            loss=np.maximum(W-.3,0)
            expected=float(evaluate_bernstein(loss_coefficients(h,.3),nodes)@masses)
            se=float(loss.std(ddof=1)/np.sqrt(N))
            rows.append(dict(h=h,law=label,N=N,exact=expected,mc=float(loss.mean()),se=se,
                             z=(loss.mean()-expected)/se if se else 0))
    pd.DataFrame(rows).to_csv(OUT/'monte_carlo.csv',index=False)
    # Broader, finite-exchangeable comparator with the same pairwise moments.
    rows=[]
    for h in [.5,.2,.1,.05,.02]:
        n=round(1/h);k=np.arange(n+1);mu=.1;rho=.05;nu=validate(mu,rho)
        loss=np.maximum(k/n-.3,0)
        lp=linprog(-loss,A_eq=np.vstack([np.ones(n+1),k,k*(k-1)]),
                   b_eq=[1,n*mu,n*(n-1)*nu],bounds=(0,None),method='highs')
        assert lp.success
        br=moment_bound(h,.3,mu,rho,512)
        rows.append(dict(h=h,mixture_upper=br.upper,finite_exchangeable=-lp.fun))
    pd.DataFrame(rows).to_csv(OUT/'assumption_sensitivity.csv',index=False)
    report={'seconds':time.time()-started,'seed':1720406,'monte_carlo_draws':6*N,
            'fixed_cash_cases':270,'bank_choice_cases':90,'curve_cases':3618,
            'exact_rational_certificates':len(certs)}
    (OUT/'run_metadata.json').write_text(json.dumps(report,indent=2))
    print(report,flush=True)

if __name__=='__main__':main()
