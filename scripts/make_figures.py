from pathlib import Path
from fractions import Fraction
import sys,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
from matplotlib.patches import FancyBboxPatch
from scipy.stats import beta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from delegated_deposits.model import *
ROOT=Path(__file__).resolve().parents[1];FIG=ROOT/'figures'
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':9,'axes.titlesize':10,
                     'axes.labelsize':9,'legend.fontsize':8,'xtick.labelsize':8,
                     'ytick.labelsize':8,'axes.spines.top':False,'axes.spines.right':False,
                     'savefig.bbox':'tight','pdf.fonttype':42,'ps.fonttype':42})
BLUE='#235789';ORANGE='#c15d24';TEAL='#238578';GRAY='#62666a'

def save(fig,name):
    fig.savefig(FIG/f'{name}.pdf');fig.savefig(FIG/f'{name}.png',dpi=180);plt.close(fig)

def main():
    fig,axes=plt.subplots(1,2,figsize=(6.7,3.0))
    for ax,groups,title in [(axes[0],8,'A. Eight separate withdrawal triggers'),
                             (axes[1],2,'B. Two shared withdrawal triggers')]:
        ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off');ax.set_title(title,loc='left',pad=12)
        for i in range(8):
            y=.86-i*.095;g=i if groups==8 else i//4
            ax.add_patch(FancyBboxPatch((.02,y-.022),.25,.048,boxstyle='round,pad=.006',
                                       ec=GRAY,fc='#f4f5f6',lw=.8))
            ax.text(.145,y+.002,f'Account {i+1}',ha='center',va='center',fontsize=7)
            yy=y if groups==8 else (.72 if g==0 else .31)
            color=BLUE if groups==8 else [BLUE,ORANGE][g]
            ax.annotate('',xy=(.5,yy),xytext=(.28,y),arrowprops=dict(arrowstyle='->',color=color,lw=.9))
        ys=[.86-i*.095 for i in range(8)] if groups==8 else [.72,.31]
        for i,y in enumerate(ys):
            color=BLUE if groups==8 else [BLUE,ORANGE][i]
            ax.add_patch(FancyBboxPatch((.5,y-.027),.43,.057,boxstyle='round,pad=.007',ec=color,fc='white'))
            ax.text(.715,y,('Trigger '+str(i+1)) if groups==8 else ('Shared trigger '+str(i+1)),ha='center',va='center',fontsize=7.5)
        ax.text(.48,.035,'Same balances, insurance, and individual withdrawal probability',ha='center',fontsize=7,wrap=True)
    fig.tight_layout(w_pad=2);save(fig,'01-ownership-and-control')

    refined=pd.read_csv(ROOT/'results/convergence.csv');sweep=pd.read_csv(ROOT/'results/moment_sweep.csv')
    fig,ax=plt.subplots(figsize=(6.5,3.5))
    for rho,color,label in [(0,BLUE,'Independent triggers'),(.05,ORANGE,'Common-state correlation 0.05'),(.2,TEAL,'Common-state correlation 0.20')]:
        frame=(sweep[(sweep.mu==.1)&(sweep.cash==.3)&(sweep.rho==0)] if rho==0
               else refined[(refined.rho==rho)&(refined.degree==4096)]).sort_values('h')
        ax.plot(frame.h,frame.lower*100,marker='o',color=color,label=label,lw=1.6,ms=4)
        ax.fill_between(frame.h,frame.lower*100,frame.upper*100,color=color,alpha=.2)
        if rho:
            ax.axhline(100*float(common_state_floor(.3,.1,rho)),color=color,ls=':',lw=1)
    ax.set(xscale='log',yscale='log',xlabel='Largest permitted controller share, h',
           ylabel='Expected uncovered withdrawals\n(% of delegated balance)')
    ax.set_xticks([.02,.05,.1,.2,.5,1],['2%','5%','10%','20%','50%','100%'])
    ax.legend(loc='lower right',frameon=False);ax.grid(axis='y',alpha=.15)
    fig.tight_layout();save(fig,'02-control-and-common-risk')

    mu=.1;rho=.05;nu=validate(mu,rho);cash=.3;d=np.sqrt((cash-mu)**2+nu-mu*mu)
    laws=[(np.array([0,nu/mu]),np.array([1-mu*mu/nu,mu*mu/nu]),BLUE,'Low-tail two-point law'),
          (np.array([cash-d,cash+d]),np.array([(cash+d-mu)/(2*d),(mu-cash+d)/(2*d)]),ORANGE,'High-tail two-point law')]
    fig,axes=plt.subplots(1,2,figsize=(6.7,3.2));p=np.linspace(0,1,1001)
    for nodes,masses,color,label in laws:
        cdf=np.sum((p[:,None]>=nodes)*masses,axis=1)
        axes[0].step(p,cdf,where='post',color=color,label=label)
    axes[0].plot(p,beta.cdf(p,mu*(1/rho-1),(1-mu)*(1/rho-1)),color=TEAL,ls='--',label='Beta law')
    axes[0].set(xlim=(0,.6),xlabel='Common withdrawal propensity, P',ylabel='Cumulative probability',title='A. Identical first two moments')
    axes[0].legend(frameon=False,loc='lower right',fontsize=6.8)
    l=np.linspace(0,.6,151)
    for nodes,masses,color,label in laws:
        loss=[evaluate_bernstein(loss_coefficients(.02,float(x)),nodes)@masses for x in l]
        axes[1].plot(l,np.array(loss)*100,color=color,label=label)
    axes[1].plot(l,[100*beta_loss(.02,float(x)) for x in l],color=TEAL,ls='--')
    axes[1].set(xlabel='Cash / delegated balance',ylabel='Expected uncovered withdrawals (%)',title='B. Different liquidity costs (h = 2%)')
    axes[1].set_ylim(0,4);axes[1].set_xlim(.15,.6)
    fig.tight_layout(w_pad=2);save(fig,'03-moments-and-tails')

    base=pd.read_csv(ROOT/'results/bank_choice.csv');new=pd.read_csv(ROOT/'results/bank_choice_refined.csv')
    fig,axes=plt.subplots(1,2,figsize=(6.7,3.2))
    for rho,color,label in [(0,BLUE,'Correlation 0'),(.05,ORANGE,'Correlation 0.05'),(.2,TEAL,'Correlation 0.20')]:
        f=(base[(base.rho==0)&(base.ratio==.2)] if rho==0 else new[new.rho==rho]).sort_values('h')
        axes[0].plot(f.h,f.cost_upper*100,marker='o',ms=3,color=color,label=label)
        axes[1].plot(f.h,f.cash*100,marker='o',ms=3,color=color)
    for ax in axes:
        ax.set_xscale('log');ax.set_xticks([.02,.1,.5,1],['2%','10%','50%','100%']);ax.set_xlabel('Largest permitted controller share, h')
    axes[0].set(title='A. Robust funding cost',ylabel='Minimum robust cost / shortage cost (%)')
    axes[1].set(title='B. Selected cash buffer',ylabel='Cash / delegated balance (%)')
    axes[0].legend(frameon=False);fig.tight_layout(w_pad=2);save(fig,'04-bank-choice')

    banks=pd.read_csv(ROOT/'data/processed/banks_20251231.csv')
    summary=pd.read_csv(ROOT/'results/bank_scenario_summary.csv')
    fig,axes=plt.subplots(1,2,figsize=(6.7,3.2))
    for field,color,label in [('cash_ratio',BLUE,'Cash and balances due'),('treasury_ratio',TEAL,'Plus Treasury securities')]:
        v=np.sort(banks[field]);axes[0].plot(v*100,np.arange(1,len(v)+1)/len(v)*100,color=color,label=label)
    axes[0].set(xlim=(0,60),ylim=(0,100),xlabel='Buffer / domestic deposits (%)',ylabel='Share of banks (%)',title='A. Observed buffer distributions')
    axes[0].legend(frameon=False,fontsize=7)
    for h,color,label in [(1.,GRAY,'100% cap'),(.2,ORANGE,'20% cap'),(.05,BLUE,'5% cap')]:
        f=summary[(summary.date==20251231)&(summary.buffer=='cash')&(summary.h==h)].sort_values('theta')
        axes[1].plot(f.theta*100,f.median_upper_bps,color=color,marker='o',label=label)
    axes[1].set(xlabel='Assumed delegated deposit share (%)',ylabel='Median envelope (deposit basis points)',title='B. Hypothetical delegation scenarios')
    axes[1].legend(frameon=False,fontsize=7);fig.tight_layout(w_pad=2);save(fig,'05-public-balance-sheets')

    certificates=json.loads((ROOT/'results/rational_certificates_refined.json').read_text())
    cert=next(c for c in certificates if c['h']=='0.02' and Fraction(c['rho'])==Fraction(1,20))
    y=np.array([float(Fraction(z)) for z in cert['dual']]);p=np.linspace(0,1,501)
    fig,axes=plt.subplots(1,2,figsize=(6.7,3.2))
    axes[0].plot(p,evaluate_bernstein(loss_coefficients(.02,.3),p),color=BLUE,label='Conditional shortage polynomial')
    axes[0].plot(p,y[0]+y[1]*p+y[2]*p*p,color=ORANGE,ls='--',label='Certified quadratic majorant')
    nodes=np.array([float(Fraction(z)) for z in cert['nodes']]);axes[0].scatter(nodes,evaluate_bernstein(loss_coefficients(.02,.3),nodes),s=18,color=TEAL,zorder=4)
    axes[0].set(xlabel='Common withdrawal propensity, P',ylabel='Conditional expected shortage',title='A. A global upper certificate')
    axes[0].legend(frameon=False,fontsize=6.8)
    for h,color in [(.2,TEAL),(.05,ORANGE),(.02,BLUE)]:
        f=refined[(refined.rho==.05)&(refined.h==h)].sort_values('degree')
        axes[1].plot(f.degree,f.gap*10000,color=color,marker='o',label=f'h = {h:.0%}')
    axes[1].set(xscale='log',yscale='log',xlabel='Bernstein degree',ylabel='Upper-lower gap (basis points)',title='B. Numerical convergence')
    axes[1].set_xticks([512,1024,2048,4096],['512','1,024','2,048','4,096']);axes[1].legend(frameon=False)
    axes[1].xaxis.set_minor_formatter(NullFormatter())
    fig.tight_layout(w_pad=2);save(fig,'06-verification')
    print('Six vector figures and PNG previews written.')

if __name__=='__main__':main()
