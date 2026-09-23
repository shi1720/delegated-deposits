"""Example treasury calculation. Scenario inputs are not estimated parameters."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from delegated_deposits.model import moment_bound,optimal_liquidity
from delegated_deposits.exposure import aggregate_authority
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--cap',type=float,default=.05)
p.add_argument('--cash',type=float,default=.3)
p.add_argument('--mean',type=float,default=.1)
p.add_argument('--correlation',type=float,default=.05)
p.add_argument('--cost-ratio',type=float,default=.2)
p.add_argument('--authority-json',help='JSON list of trigger_id / authorized_balance records.')
a=p.parse_args()
exposure=None
if a.authority_json:
    exposure=aggregate_authority(json.loads(Path(a.authority_json).read_text()))
    a.cap=exposure['cap']
if a.cap<.005:raise SystemExit('This demonstration is limited to caps of at least 0.5%; use the analytical floor for finer structures.')
b=moment_bound(a.cap,a.cash,a.mean,a.correlation,4096)
c=optimal_liquidity(a.cap,a.mean,a.correlation,a.cost_ratio,4096)
print(json.dumps({'scenario':vars(a),'authority_summary':exposure,'fixed_cash_expected_shortage':{'lower':b.lower,'upper':b.upper},
                  'selected_cash':c['cash'],'minimum_cost':{'lower':c['cost_lower'],'upper':c['cost_upper']},
                  'units':'Fractions of the delegated balance; cost normalized by incremental shortage cost.'},indent=2))
