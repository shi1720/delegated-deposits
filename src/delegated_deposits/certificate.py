"""Exact rational certificates for selected fixed-cash upper and lower bounds.

This independently verifies an LP's proposal using Python integers/Fractions.
It does not invoke the LP solver or trust floating-point feasibility flags.
"""
from fractions import Fraction as F
from math import comb


def rat(x):
    return F(str(x))


def coefficients(h,cash):
    h,cash=rat(h),rat(cash)
    q=1//h;rem=1-q*h
    if rem==0:
        return [max(F(k,q)-cash,0) for k in range(q+1)]
    m=q+1
    return [F(m-k,m)*max(k*h-cash,0)+F(k,m)*max((k-1)*h+rem-cash,0)
            for k in range(m+1)]


def solve3(A,b):
    A=[list(row)+[v] for row,v in zip(A,b)]
    for k in range(3):
        j=next(i for i in range(k,3) if A[i][k])
        A[k],A[j]=A[j],A[k]
        pivot=A[k][k];A[k]=[x/pivot for x in A[k]]
        for i in range(3):
            if i!=k:
                v=A[i][k];A[i]=[x-v*y for x,y in zip(A[i],A[k])]
    return [row[-1] for row in A]


def exact_certificate(h,cash,mu,rho,bound):
    mu,rho=rat(mu),rat(rho);nu=mu*mu+rho*mu*(1-mu)
    c=coefficients(h,cash);n=len(c)-1;N=bound.degree
    if len(bound.dual)!=3:raise ValueError('Certificate is for interior moments.')
    y=[rat(v) for v in bound.dual]
    slack=[]
    for k in range(N+1):
        elevated=sum((c[j]*F(comb(k,j)*comb(N-k,n-j),comb(N,n))
                      for j in range(max(0,k-N+n),min(n,k)+1)),F(0))
        slack.append(y[0]+y[1]*F(k,N)+y[2]*F(k*(k-1),N*(N-1))-elevated)
    repair=max(F(0),-min(slack));y[0]+=repair
    upper=y[0]+y[1]*mu+y[2]*nu
    nodes=[rat(v) for v in bound.nodes]
    if len(nodes)==3:
        masses=solve3([[F(1)]*3,nodes,[p*p for p in nodes]],[F(1),mu,nu])
    elif len(nodes)==2:
        a,b=nodes;masses=[(b-mu)/(b-a),(mu-a)/(b-a)]
    else:
        raise ValueError('Expected two or three support points.')
    # Float proposals with only two support points may need a third exact node.
    if sum(a*b*b for a,b in zip(masses,nodes))!=nu:
        nodes=[F(0),nu/mu,F(1)]
        masses=solve3([[F(1)]*3,nodes,[p*p for p in nodes]],[F(1),mu,nu])
    assert min(masses)>=0 and sum(masses)==1
    assert sum(a*b for a,b in zip(masses,nodes))==mu
    assert sum(a*b*b for a,b in zip(masses,nodes))==nu
    losses=[sum(c[j]*comb(n,j)*p**j*(1-p)**(n-j) for j in range(n+1)) for p in nodes]
    lower=sum(a*b for a,b in zip(masses,losses))
    assert lower<=upper
    return {'h':str(h),'cash':str(cash),'mu':str(mu),'rho':str(rho),'degree':N,
            'dual':[str(z) for z in y],'nodes':[str(z) for z in nodes],
            'masses':[str(z) for z in masses],'lower':str(lower),'upper':str(upper),
            'upper_float':float(upper),'lower_float':float(lower),
            'exact_repair':str(repair),'minimum_coefficient_slack':str(min(slack)+repair)}


def verify(cert):
    from types import SimpleNamespace
    br=SimpleNamespace(dual=cert['dual'],nodes=cert['nodes'],degree=cert['degree'])
    check=exact_certificate(cert['h'],cert['cash'],cert['mu'],cert['rho'],br)
    assert F(check['upper'])==F(cert['upper'])
    assert F(check['lower'])==F(cert['lower'])
    return True
