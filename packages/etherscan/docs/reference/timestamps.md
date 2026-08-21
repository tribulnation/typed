# Timestamps

Etherscan's wire timestamps are Unix seconds. This client converts them to `datetime` on
exactly one request parameter, and leaves everything else as the raw wire value.

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

A `timeStamp` field on a response row (`account.transactions`, `account.mined_blocks`,
`blocks.reward`, `l2.plasma_deposits`, ...) comes back as an unconverted wire string — Unix
seconds as text, no `datetime` conversion applied. Parse one with the same converter the
request side uses internally:

```python
from typed_etherscan.core import timestamp_seconds

raw = '1578638524'  # a `timeStamp` field, exactly as Etherscan returns it
when = timestamp_seconds.parse(raw)  # -> datetime, UTC
```

`timestamp_seconds.dump(a_datetime)` is the reverse: it's what `number_by_time` calls
internally to turn your `datetime` back into the epoch-seconds string Etherscan expects.
