# Manage Account Data

`account` reads need credentials — see [API Keys Setup](../api-keys.md).

## Account Summary

```python
from deribit import Deribit

async with Deribit.new(testnet=True) as client:
  summary = await client.http.account.get_account_summary(currency='BTC')
  print(summary['balance'], summary['equity'], summary['available_funds'])
```

## Open Positions

```python
from deribit import Deribit

async with Deribit.new(testnet=True) as client:
  positions = await client.http.account.get_positions(currency='BTC', kind='future')
  for position in positions:
    print(position['instrument_name'], position['size'], position['direction'])
```

## Transaction Log

```python
from deribit import Deribit

async with Deribit.new(testnet=True) as client:
  log = await client.http.account.get_transaction_log(
    currency='BTC', start_timestamp=1700000000000, end_timestamp=1700086400000,
  )
  print(log['logs'])
```

`get_transaction_log` also has a `get_transaction_log_paged` sibling — see
[Paginate Through Results](paginate-through-results.md).
