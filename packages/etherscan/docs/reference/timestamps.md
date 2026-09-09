# Timestamps

Etherscan's wire timestamps are Unix seconds. This client converts them to `datetime` on
one request parameter and on the response rows listed below, and leaves the rest as the raw
wire value.

## Request Side

`blocks.number_by_time`'s `timestamp` parameter is the one place a real `datetime` goes in
directly:

```python
from datetime import datetime, timezone
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  closest = await client.blocks.number_by_time(
    timestamp=datetime(2020, 1, 10, tzinfo=timezone.utc), closest='before',
  )
```

## Response Side

The `timeStamp` field of the account feeds (`account.transactions`, `erc20_transfers`,
`erc721_transfers`, `erc1155_transfers`, `internal_transactions`,
`internal_transactions_by_block_range`) and of the `l2` rows comes back as a UTC
`datetime`, converted from Etherscan's epoch-seconds string:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  txs = await client.account.transactions(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
  first = txs['result'][0]['timeStamp']  # datetime, UTC
```

A `timeStamp` on any other row (`account.mined_blocks`, `blocks.reward`, ...) is still the
unconverted wire string, Unix seconds as text. Parse one with the same converter the client
uses internally:

```python
from typed_etherscan.core import timestamp_seconds

raw = '1578638524'  # a `timeStamp` field, exactly as Etherscan returns it
when = timestamp_seconds.parse(raw)  # -> datetime, UTC
```

`timestamp_seconds.dump(a_datetime)` is the reverse: it's what `number_by_time` calls
internally to turn your `datetime` back into the epoch-seconds string Etherscan expects.
