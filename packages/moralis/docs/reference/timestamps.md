# Timestamps

Moralis has no timestamp handling at all: no `EpochConverter`, no `datetime`-typed
field, and no conversion helper anywhere in the client. Every timestamp is a plain
string, passed straight through in whatever format the underlying Moralis API uses.

## Common Patterns

Response fields such as `block_timestamp` are typed `str` and returned exactly as
Moralis sends them, with no client-side parsing.

Request filters such as `from_date`/`to_date` are typed `str | None` and are sent to
Moralis exactly as given, with no client-side formatting.

```python
from moralis import Moralis

async with Moralis.new() as client:
  history = await client.evm.wallet.history(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045',
    chain='eth',
    from_date='2024-01-01',
    to_date='2024-02-01',
  )
  print(history['result'][0].get('block_timestamp'))
```
