# Manage Account Data

dYdX account state is split across wallet-level chain accounts and
subaccount-level trading state. Use chain modules for wallet balances and
protocol state; use the indexer for trading history, fills, transfers, and
positions.

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  balances = await client.chain.bank.all_balances('dydx1...', resolve_denom=False)
  print(balances)
```

Subaccount trading state is available from both the indexer and chain modules:

```python
from typed_dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  subaccount = await client.indexer.data.get_subaccount(address, subaccount=0)
  chain_subaccount = await client.chain.subaccounts.subaccount(address, number=0)
  print(subaccount, chain_subaccount)
```

For history, use the indexer:

```python
from typed_dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  fills = await client.indexer.data.get_fills(address=address, subaccount=0, limit=100)
  transfers = await client.indexer.data.get_transfers(address, subaccount=0, limit=100)
  positions = await client.indexer.data.list_positions(address, subaccount=0)
  print(fills, transfers, positions)
```

Read-only account workflows can use `public=True`. Signed workflows need a
mnemonic; see [Wallet Setup](../authenticated-setup.md).

## Position Trade History

`get_trade_history` returns position actions with entry prices, execution prices, fees,
and realized PnL. It is public and needs only a wallet address and subaccount number.
`get_parent_trade_history` includes the parent's child subaccounts; each row identifies
its child through `subaccountNumber`.

```python
from typed_dydx import Indexer

address = 'dydx1...'

async with Indexer.mainnet() as indexer:
  history = await indexer.data.get_trade_history(
    address=address,
    subaccount=0,
    market='BTC-USD',
    market_type='PERPETUAL',
    limit=100,
    page=1,
  )
  for trade in history['tradeHistory']:
    print(trade['time'], trade['action'], trade['netRealizedPnl'])

  parent_history = await indexer.data.get_parent_trade_history(
    address=address,
    parent_subaccount=0,
    limit=100,
  )
  print(parent_history['tradeHistory'])
```

Supply `market` and `market_type` together, or omit both to query all markets.
An incomplete pair raises `ValueError` before sending a request. Amounts validate to
`Decimal` and `time` to a timezone-aware `datetime` by default.

Actions are `OPEN`, `EXTEND`, `PARTIAL_CLOSE`, `CLOSE`, `LIQUIDATION_PARTIAL_CLOSE`, or
`LIQUIDATION_CLOSE`. A reversal creates separate close and open rows. The returned
`positionSide` describes the position after the action and is `None` when fully closed.
`additionalSize` is positive for a buy and negative for a sell, including closing trades.
Treat `id` as an opaque string; it can include a block height and an open/close suffix.

**Do not sum `netFee` or `netRealizedPnl` across rows.** Both are cumulative within each
child subaccount's market position lifecycle. Realized PnL excludes trading fees and
funding payments. `netRealizedPnlPercent` is a ratio (`0.01` means 1%), and can be `None`.
For a complete account ledger, also retrieve fills, funding payments, and transfers.

Results are newest first. Use `page` for a single page, or the
[`get_trade_history_paged` and `get_parent_trade_history_paged` helpers](paginate-through-results.md#trade-history)
for a walk. There are no date or height filters. Queries exceeding 100,000 matching
underlying fills fail before pagination; a market filter can narrow the query, while a
smaller `limit` cannot avoid that bound. Pages are not a fixed snapshot: new trades during
a walk can shift rows between pages.
