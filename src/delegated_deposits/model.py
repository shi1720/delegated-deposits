"""Exact control aggregation and constructive bounds for a moment problem.

No parameter in this module is estimated from observed bank withdrawals.
The LP upper bound dominates a polynomial on the WHOLE unit interval by
its Bernstein coefficients. Grid feasibility alone is not an upper bound.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
import math
import numpy as np
from scipy.optimize import linprog
from scipy.stats import binom, betabinom


def validate(mu, rho):
    if not (0 < mu < 1 and 0 <= rho <= 1):
        raise ValueError('Require 0 < mu < 1 and 0 <= rho <= 1.')
    return mu * mu + rho * mu * (1 - mu)


def capped_weights(h):
    if not 0 < h <= 1:
        raise ValueError('A share cap must lie in (0,1].')
    q = int(math.floor(1 / h + 1e-12))
    remainder = 1 - q * h
    if remainder < 1e-11:
        return np.full(q, 1 / q)
    return np.r_[np.full(q, h), remainder]


def cash_knots(h):
    w = capped_weights(h)
    q = len(w)
    if np.allclose(w, w[0], atol=1e-13, rtol=0):
        return np.linspace(0, 1, q + 1)
    return np.unique(np.round(np.r_[np.arange(q)*h,
                                     np.arange(q)*h+w[-1]], 13))


def loss_coefficients(h, cash):
    """Bernstein coefficients conditioning on the total number of triggers."""
    if not 0 <= cash <= 1:
        raise ValueError('Cash is normalized to the delegated balance.')
    w = capped_weights(h)
    n = len(w)
    k = np.arange(n+1)
    if np.allclose(w, w[0], atol=1e-13, rtol=0):
        return np.maximum(k / n - cash, 0)
    return ((n-k)/n*np.maximum(k*h-cash, 0)
            + k/n*np.maximum((k-1)*h+w[-1]-cash, 0))


def evaluate_bernstein(coeff, p):
    p = np.asarray(p)
    n = len(coeff)-1
    return binom.pmf(np.arange(n+1), n, p[..., None]) @ coeff


@lru_cache(maxsize=32)
def elevation_matrix(n, degree):
    if degree < n:
        raise ValueError('Cannot lower the Bernstein degree.')
    # Hypergeometric probabilities; exact integer binomial coefficients avoid
    # the overflow that a naive floating factorial implementation produces.
    mat = np.zeros((degree+1, n+1))
    for k in range(degree+1):
        for j in range(max(0, k-degree+n), min(n,k)+1):
            mat[k,j] = (math.comb(k,j)*math.comb(degree-k,n-j)
                        / math.comb(degree,n))
    return mat


@dataclass
class Bound:
    lower: float
    upper: float
    nodes: np.ndarray
    masses: np.ndarray
    dual: np.ndarray
    degree: int
    moment_residual: float

    @property
    def gap(self):
        return self.upper-self.lower


def moment_bound(h, cash, mu=.1, rho=.05, degree=256, grid_size=1001):
    nu = validate(mu, rho)
    coeff = loss_coefficients(h, cash)
    if rho == 0 or rho == 1:
        nodes = np.array([mu]) if rho == 0 else np.array([0.,1.])
        masses = np.array([1.]) if rho == 0 else np.array([1-mu,mu])
        value = float(evaluate_bernstein(coeff,nodes) @ masses)
        return Bound(value,value,nodes,masses,np.array([]),0,0.)
    n = len(coeff)-1
    degree = max(degree,n,2)
    nodes = np.unique(np.r_[np.linspace(0,1,grid_size),mu,
                            nu/mu,(mu-nu)/(1-mu)])
    A = np.vstack([np.ones_like(nodes),nodes,nodes**2])
    b = np.array([1.,mu,nu])
    objective = evaluate_bernstein(coeff,nodes)
    primal = linprog(-objective,A_eq=A,b_eq=b,bounds=(0,None),method='highs',
                     options={'dual_feasibility_tolerance':1e-9,
                              'primal_feasibility_tolerance':1e-9})
    if not primal.success:
        raise RuntimeError(primal.message)
    k = np.arange(degree+1)
    Q = np.c_[np.ones(degree+1),k/degree,k*(k-1)/(degree*(degree-1))]
    elevated = elevation_matrix(n,degree) @ coeff
    dual = linprog(b,A_ub=-Q,b_ub=-elevated,bounds=[(None,None)]*3,
                   method='highs')
    if not dual.success:
        raise RuntimeError(dual.message)
    y = dual.x.copy()
    # Numerical feasibility repair. Exact rational verification is separate.
    y[0] += max(0.,float(np.max(elevated-Q@y))) + 1e-12
    keep = primal.x > 1e-10
    residual = float(np.max(np.abs(A[:,keep]@primal.x[keep]-b)))
    lower, upper = float(-primal.fun),float(b@y)
    if residual > 1e-7 or upper < lower-1e-8:
        raise ArithmeticError('Failed moment/duality audit.')
    return Bound(lower,upper,nodes[keep],primal.x[keep],y,degree,residual)


def common_state_floor(cash, mu=.1, rho=.05):
    """Sharp bounded-support two-moment stop-loss bound (classical)."""
    nu = validate(mu,rho)
    t = np.asarray(cash)
    if rho == 0:
        return np.maximum(mu-t,0)
    variance = nu-mu*mu
    a = nu/(2*mu)
    b = (1-nu)/(2*(1-mu))
    middle = (np.sqrt((t-mu)**2+variance)+mu-t)/2
    return np.where(t<a,mu-t*mu*mu/nu,
                    np.where(t>b,(1-t)*variance/(1-2*mu+nu),middle))


def beta_loss(h,cash,mu=.1,rho=.05):
    coeff=loss_coefficients(h,cash)
    if rho == 0:
        return float(evaluate_bernstein(coeff,mu))
    if rho == 1:
        return mu*(1-cash)
    a,b=mu*(1/rho-1),(1-mu)*(1/rho-1)
    return float(betabinom.pmf(np.arange(len(coeff)),len(coeff)-1,a,b)@coeff)


def enumerate_distribution(weights,p):
    weights=np.asarray(weights,dtype=float)
    if len(weights)>20 or np.any(weights<0) or not 0<=p<=1:
        raise ValueError('Invalid enumeration input.')
    states=np.array(list(product([0,1],repeat=len(weights))))
    count=states.sum(axis=1)
    probs=p**count*(1-p)**(len(weights)-count)
    return states@weights,probs


def optimal_liquidity(h,mu=.1,rho=.05,ratio=.2,degree=256):
    if not 0 < ratio < 1:
        raise ValueError('Require 0 < opportunity/shortage cost < 1.')
    nu=validate(mu,rho)
    support=cash_knots(h)
    if rho in (0,1):
        values=[ratio*l+moment_bound(h,l,mu,rho).upper for l in support]
        j=int(np.argmin(values)); value=float(values[j])
        return {'cash':float(support[j]),'cost_upper':value,'cost_lower':value,
                'optimizer_gap':0.,'bound':moment_bound(h,support[j],mu,rho)}
    # One LP jointly chooses cash, positive-part epigraphs, and the polynomial
    # majorant. Unlike a knot-only cash search, it permits an interior optimum.
    w=capped_weights(h); m=len(w); n=len(support); degree=max(degree,m,2)
    B=np.zeros((m+1,n))
    if np.allclose(w,w[0],atol=1e-13,rtol=0): B=np.eye(n)
    else:
        for k in range(m+1):
            if k<m: B[k,np.argmin(abs(support-k*h))]+=(m-k)/m
            if k>0: B[k,np.argmin(abs(support-((k-1)*h+w[-1])))]+=k/m
    E=elevation_matrix(m,degree)@B
    k=np.arange(degree+1)
    Q=np.c_[np.ones(degree+1),k/degree,k*(k-1)/(degree*(degree-1))]
    b=np.array([1.,mu,nu])
    A1=np.c_[-np.ones(n),-np.eye(n),np.zeros((n,3))]
    A2=np.c_[np.zeros(degree+1),E,-Q]
    upper=linprog(np.r_[ratio,np.zeros(n),b],A_ub=np.vstack([A1,A2]),
                  b_ub=np.r_[-support,np.zeros(degree+1)],
                  bounds=[(0,1)]+[(0,None)]*n+[(None,None)]*3,method='highs')
    if not upper.success:raise RuntimeError(upper.message)
    # Minimax lower bound: a common-state law on a finite grid maximizes the
    # bank's minimum cost. For a FIXED law, checking cash knots is sufficient.
    nodes=np.unique(np.r_[np.linspace(0,1,1001),mu,nu/mu,(mu-nu)/(1-mu)])
    losses=np.array([evaluate_bernstein(loss_coefficients(h,l),nodes) for l in support])
    primal=linprog(np.r_[np.zeros(len(nodes)),-1.],
                   A_ub=np.c_[-losses,np.ones(n)],b_ub=ratio*support,
                   A_eq=np.c_[np.vstack([np.ones_like(nodes),nodes,nodes**2]),np.zeros(3)],
                   b_eq=b,bounds=[(0,None)]*len(nodes)+[(None,None)],method='highs')
    if not primal.success:raise RuntimeError(primal.message)
    cash=float(upper.x[0]); br=moment_bound(h,cash,mu,rho,degree)
    # Directly re-evaluating the selected cash can tighten the upper bound.
    cost=ratio*cash+br.upper
    return {'cash':cash,'cost_upper':cost,'cost_lower':float(-primal.fun),
            'optimizer_gap':cost+float(primal.fun),'bound':br}


def withdrawal_pmf(h,nodes,masses):
    w=capped_weights(h)
    m=len(w)
    nodes=np.asarray(nodes);masses=np.asarray(masses)
    support=cash_knots(h)
    if np.allclose(w,w[0],atol=1e-13,rtol=0):
        probabilities=masses@binom.pmf(np.arange(m+1)[None,:],m,nodes[:,None])
        return support,probabilities
    q=m-1
    probs0=masses@(binom.pmf(np.arange(q+1)[None,:],q,nodes[:,None])*(1-nodes[:,None]))
    probs1=masses@(binom.pmf(np.arange(q+1)[None,:],q,nodes[:,None])*nodes[:,None])
    prob=np.zeros(len(support))
    for x,z in zip(np.r_[np.arange(q+1)*h,np.arange(q+1)*h+w[-1]],np.r_[probs0,probs1]):
        prob[np.argmin(abs(support-x))]+=z
    return support,prob
