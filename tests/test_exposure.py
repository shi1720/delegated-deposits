import pytest
from delegated_deposits.exposure import aggregate_authority

def test_account_splitting_does_not_diversify_control():
    a=aggregate_authority([{'trigger_id':'a','authorized_balance':60},{'trigger_id':'b','authorized_balance':40}])
    b=aggregate_authority([{'trigger_id':'a','authorized_balance':20}]*3+[{'trigger_id':'b','authorized_balance':40}])
    assert a==b and a['cap']==.6

@pytest.mark.parametrize('value',[-1,float('nan'),float('inf')])
def test_invalid_balance(value):
    with pytest.raises(ValueError):aggregate_authority([{'trigger_id':'a','authorized_balance':value}])

def test_empty_balance():
    with pytest.raises(ValueError):aggregate_authority([])
