# Timestamps

Where Alchemy declares a wire timestamp format, the client renders it as a real Python
`datetime` end to end: pass a `datetime` in, get a `datetime` back. No manual conversion
needed on either side.

## Request Parameters

`prices.historical`'s `startTime`/`endTime` window bounds are Unix epoch seconds on the
wire, typed as `datetime`:

```python
from datetime import datetime, timedelta, timezone
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  end = datetime.now(timezone.utc)
  start = end - timedelta(days=1)
  history = await client.prices.historical({
    'symbol': 'ETH',
    'startTime': start,
    'endTime': end,
  })
```

## Response Fields

These response fields are RFC 3339 strings on the wire and validate into `datetime`
automatically:

- Prices' `lastUpdatedAt` (`prices.by_symbol`, `prices.by_address`) and each historical
  price point's `timestamp` (`prices.historical`)
- NFT's `lastIngestedAt` (`nft(...).get_contract_metadata`) and `retrievedAt`
  (`nft(...).get_floor_price`)
- Transfers' `blockTimestamp` (`transfers(...).get_asset_transfers`, present when
  `withMetadata=True`)
- Portfolio's `lastUpdatedAt` on each token price snapshot (`portfolio.tokens`)

## Fields Alchemy Doesn't Document A Fixed Format For

A few timestamp-shaped fields stay plain strings, because Alchemy publishes no fixed wire
format for them: NFT metadata's `timeLastUpdated` and mint `timestamp`
(`nft(...).get_nft_metadata` and related), Portfolio NFT's `acquiredAt.blockTimestamp`, and
transaction history's `timeStamp` (`portfolio.transactions.history`). Parse these yourself
if you need a `datetime` — a guessed format would risk rejecting valid responses.
