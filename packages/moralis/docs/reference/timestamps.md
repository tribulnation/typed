# Timestamps

Response fields that carry a timestamp are typed as real `datetime` (or, for a plain
calendar date, `date`) values, not raw strings or integers. The client converts each one
from the wire format Moralis actually uses for that field -- which varies by endpoint --
so you never call `datetime.fromtimestamp(...)` yourself.

## Wire Formats

| Wire shape | Type | Example field |
| --- | --- | --- |
| RFC 3339 string | `TimestampIso` | `evm.wallet.history`'s `block_timestamp` |
| Unix milliseconds | `TimestampMillis` | `evm.price.token_price`'s `blockTimestamp` |
| Unix seconds | `TimestampSeconds` | `bitcoin.blockchain.block`'s `blockTime`/`time` |
| Plain calendar date | `DateIso` | `evm.nft.metadata.collection_metadata`'s `created_date` |

Most response timestamps are `TimestampIso`; the others show up where Moralis's own API
genuinely returns seconds, milliseconds, or a bare date for that particular field.

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  history = await client.evm.wallet.history(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  when = history['result'][0]['block_timestamp']
  print(when.isoformat())  # a real datetime, already parsed
```

## Request-Side Date Filters

Some endpoints' own date-range filters -- `evm.wallet.history`'s `from_date`/`to_date`,
for example -- stay plain `str | None` on purpose: Moralis's docs state these accept
*either* a Unix-seconds string or a date string interchangeably, so there is no single
wire format to convert to or from. Pass whichever shape you have; the value is sent to
Moralis exactly as given.

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  history = await client.evm.wallet.history(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045',
    chain='eth',
    from_date='2024-01-01',
    to_date='2024-02-01',
  )
```
