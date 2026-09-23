"""Audit archived provenance, exact certificates, sample flows, and numerical gaps."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from delegated_deposits.certificate import verify
ROOT=Path(__file__).resolve().parents[1]
meta=list((ROOT/'data/raw').glob('*.meta.json'))
assert len(meta)==7
for path in meta:
    data=json.loads(path.read_text());raw=Path(str(path).removesuffix('.meta.json'))
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==data['sha256']
    assert raw.stat().st_size==data['bytes']
protocol=json.loads((ROOT/'results/protocol_hash.json').read_text())
assert hashlib.sha256((ROOT/'notes/protocol.md').read_bytes()).hexdigest()==protocol['sha256']
count=0
for name in ['rational_certificates.json','rational_certificates_refined.json']:
    for certificate in json.loads((ROOT/'results'/name).read_text()):
        assert verify(certificate);count+=1
fixed=pd.read_csv(ROOT/'results/moment_sweep.csv')
assert len(fixed)==270 and fixed.moment_residual.max()<1e-7
assert (fixed.lower<=fixed.upper+1e-9).all()
assert np.isfinite(fixed.select_dtypes('number')).all().all()
refined=pd.read_csv(ROOT/'results/convergence.csv');last=refined[refined.degree==4096]
assert len(last)==18 and last.gap.max()<.000027
choice=pd.read_csv(ROOT/'results/bank_choice_refined.csv')
assert len(choice)==18 and choice.optimizer_gap.max()<.000038
assert choice.optimizer_gap.min()>-1e-9
flow=pd.read_csv(ROOT/'results/sample_flow.csv')
assert list(flow.retained)==[4336,4485,4704]
assert (flow.raw-flow.not_insured_domestic_bank-flow.invalid_balance_sheet==flow.retained).all()
mc=pd.read_csv(ROOT/'results/monte_carlo.csv')
assert mc.N.sum()==6_000_000 and mc.z.abs().max()<4
for date in [20251231,20241231,20221231]:
    data=pd.read_csv(ROOT/f'data/processed/banks_{date}.csv')
    assert data.CERT.is_unique and (data.INSFDIC==1).all()
    assert (~data.BKCLASS.isin(['NC','OI'])).all()
    assert (data.DEPDOM>0).all() and (data.ASSET>0).all() and (data.CHBAL>=0).all()
print(f'PASS: {len(meta)} input hashes; {count} rational certificates; sample flow; numerical brackets; 6,000,000 draws.')
