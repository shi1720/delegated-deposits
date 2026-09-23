"""Aggregate stated execution authority; do not infer it from vendor identity."""
import math

def aggregate_authority(records):
    totals={}
    for row in records:
        trigger=row['trigger_id']
        balance=float(row['authorized_balance'])
        if not isinstance(trigger,str) or not trigger or not math.isfinite(balance) or balance<0:
            raise ValueError('Require a nonempty trigger ID and finite, nonnegative balance.')
        totals[trigger]=totals.get(trigger,0)+balance
    total=sum(totals.values())
    if total<=0:raise ValueError('Total authorized balance must be positive.')
    shares={k:v/total for k,v in sorted(totals.items()) if v>0}
    return {'total_authorized_balance':total,'controller_shares':shares,
            'cap':max(shares.values()),'control_hhi':sum(v*v for v in shares.values())}
