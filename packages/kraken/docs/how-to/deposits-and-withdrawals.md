# Deposits & Withdrawals

`spot.funding` -- private, see [API Keys Setup](../api-keys.md) first.

## Deposit

```python
from typed_kraken import Kraken

async with Kraken.new() as client:
  methods = await client.spot.funding.deposit_methods(asset='XBT')
  addresses = await client.spot.funding.deposit_addresses(
    asset='XBT', method=methods[0]['method'],
  )
  status = await client.spot.funding.deposit_status(asset='XBT')
```

`deposit_addresses` returns your existing deposit address for the method; pass `new=True`
to generate a fresh one where the method supports it. `deposit_status` lists recent
deposits, most recent first -- pass `cursor=True` on the first call and its returned
`next_cursor` on subsequent calls to page through more.

## Withdraw

```python
from typed_kraken import Kraken

async with Kraken.new() as client:
  methods = await client.spot.funding.withdraw_methods(asset='XBT')
  addresses = await client.spot.funding.withdraw_addresses(asset='XBT')
  info = await client.spot.funding.withdraw_info(asset='XBT', key='my-saved-address', amount='0.001')
  receipt = await client.spot.funding.withdraw(asset='XBT', key='my-saved-address', amount='0.001')
  status = await client.spot.funding.withdraw_status(asset='XBT')
  await client.spot.funding.withdraw_cancel(asset='XBT', refid=receipt['refid'])
```

`withdraw`/`withdraw_info` take an address *key name*, not a raw address -- Kraken
requires the destination to already be a pre-approved, whitelisted withdrawal address on
the account (see [API Keys Setup](../api-keys.md#withdrawal-addresses)). `withdraw_info`
previews the fee/amount a withdrawal would incur without submitting it. A pending
withdrawal can be cancelled with `withdraw_cancel` while it's still queued.
