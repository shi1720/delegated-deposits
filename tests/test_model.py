from itertools import product
import numpy as np
import pytest
from delegated_deposits.model import (capped_weights,loss_coefficients,
    evaluate_bernstein,enumerate_distribution,moment_bound,common_state_floor,
    beta_loss,optimal_liquidity,elevation_matrix,withdrawal_pmf)

@pytest.mark.parametrize('h',[1,.5,.4,.3,.2,.15])
@pytest.mark.parametrize('p',[.01,.1,.5,.9])
def test_coefficients_against_enumeration(h,p):
    w=capped_weights(h); x,prob=enumerate_distribution(w,p)
    assert sum(w)==pytest.approx(1)
    assert max(w)<=h+1e-12
    for cash in [0,.03,.2,.47,.9,1]:
        actual=prob@np.maximum(x-cash,0)
        assert evaluate_bernstein(loss_coefficients(h,cash),p)==pytest.approx(actual,abs=1e-12)
    support,pmf=withdrawal_pmf(h,[p],[1])
    assert pmf.sum()==pytest.approx(1)
    assert support@pmf==pytest.approx(p)
    assert pmf@np.maximum(support-.23,0)==pytest.approx(prob@np.maximum(x-.23,0))

@pytest.mark.parametrize('h',[.4,.2,.1,.02])
def test_elevation(h):
    c=loss_coefficients(h,.237)
    e=elevation_matrix(len(c)-1,128)@c
    for p in [0,.03,.6,.91,1]:
        assert evaluate_bernstein(e,p)==pytest.approx(evaluate_bernstein(c,p),abs=1e-12)

@pytest.mark.parametrize('rho',[0,.01,.05,.2,1])
def test_moment_brackets_and_beta(rho):
    br=moment_bound(.2,.3,.1,rho)
    assert br.lower<=br.upper+1e-9
    assert br.upper>=beta_loss(.2,.3,.1,rho)-1e-9
    assert br.upper>=common_state_floor(.3,.1,rho)-1e-9
    assert br.upper<=.1+1e-9
    assert br.moment_residual<1e-7
    if rho not in (0,1):
        coeff=loss_coefficients(.2,.3)
        p=np.linspace(0,1,10001)
        assert np.min(br.dual[0]+br.dual[1]*p+br.dual[2]*p*p-evaluate_bernstein(coeff,p))>=-1e-9

@pytest.mark.parametrize('rho',[.01,.05,.2])
def test_small_cap_floor_and_limit(rho):
    mu=.1;nu=mu*mu+rho*mu*(1-mu)
    for cash in [.01,.1,.3,.8,.99]:
        br=moment_bound(.02,cash,mu,rho,degree=512)
        floor=common_state_floor(cash,mu,rho)
        assert br.lower>=floor-2e-5
        assert br.upper<=floor+.5*np.sqrt(.02*(mu-nu))+1e-4

def test_same_marginal_one_controller():
    for rho in [0,.05,.9,1]:
        br=moment_bound(1,.3,.1,rho)
        assert br.lower==pytest.approx(.07,abs=1e-8)
        assert br.upper==pytest.approx(.07,abs=1e-8)

def test_common_shock_erases_cap_benefit():
    for h in [1,.4,.1,.02]:
        assert moment_bound(h,.4,.1,1).upper==pytest.approx(.06)

def test_concentration_does_not_order_lending():
    diverse=optimal_liquidity(.02,.1,0,.2)
    one=optimal_liquidity(1,.1,0,.2)
    assert one['cash']<diverse['cash']
    assert one['cost_upper']>diverse['cost_upper']

def test_robust_bank_global_bracket():
    sol=optimal_liquidity(.2,.1,.05,.2)
    assert sol['cost_lower']<=sol['cost_upper']+1e-9
    assert sol['optimizer_gap']<2e-4
    for cash in np.linspace(0,1,31):
        assert .2*cash+moment_bound(.2,cash,.1,.05).upper>=sol['cost_lower']-1e-9

def test_pairwise_statistics_do_not_determine_tail():
    mu=.1;rho=.05;nu=mu*mu+rho*mu*(1-mu)
    low_nodes=np.array([0,nu/mu]);low_mass=np.array([1-mu*mu/nu,mu*mu/nu])
    t=.3;d=np.sqrt((t-mu)**2+nu-mu*mu)
    high_nodes=np.array([t-d,t+d]); high_mass=np.array([(t+d-mu)/(2*d),(mu-t+d)/(2*d)])
    for nodes,mass in [(low_nodes,low_mass),(high_nodes,high_mass)]:
        assert mass@nodes==pytest.approx(mu)
        assert mass@(nodes**2)==pytest.approx(nu)
    assert low_mass@np.maximum(low_nodes-t,0)==0
    assert high_mass@np.maximum(high_nodes-t,0)>0

def test_cap_majorization_random_feasible_vectors():
    rng=np.random.default_rng(1720406)
    for _ in range(30):
        # Split extreme-cap weights, a refinement preserving sum and cap.
        base=capped_weights(.3)
        fractions=rng.uniform(.1,.9,len(base))
        split=np.r_[base*fractions,base*(1-fractions)]
        for p in [.05,.2,.8]:
            x,pr=enumerate_distribution(split,p)
            for l in [.1,.3,.6]:
                refined=pr@np.maximum(x-l,0)
                extreme=evaluate_bernstein(loss_coefficients(.3,l),p)
                assert refined<=extreme+1e-12
