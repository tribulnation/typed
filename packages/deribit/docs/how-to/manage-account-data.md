# Manage Account Data

`account` reads need credentials — see [API Keys Setup](../api-keys.md).

## Account Summary

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  summary = await client.account.get_account_summary(currency='BTC')
  print(summary['balance'], summary['equity'], summary['available_funds'])
```

## Open Positions

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  positions = await client.account.get_positions(currency='BTC', kind='future')
  for position in positions:
    print(position['instrument_name'], position['size'], position['direction'])
```

## Transaction Log

```python
from datetime import datetime, timezone
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  log = await client.account.get_transaction_log(
    currency='BTC',
    start_timestamp=datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc),
    end_timestamp=datetime(2023, 11, 15, 22, 13, 20, tzinfo=timezone.utc),
  )
  print(log['logs'])
```

`get_transaction_log` also has a `get_transaction_log_paged` sibling — see
[Paginate Through Results](paginate-through-results.md).
