# Place & Manage Orders

Writes need an agent key (see [Wallet & Agent Setup](../authenticated-setup.md)); a
read-only API key cannot place orders.

gTrade is non-custodial: orders and positions live in the chain's Diamond contract. A
write checks the agent's scope, simulates the request and returns the order with an
**unsigned EVM transaction**. The client never signs or broadcasts and takes no RPC
URL: the agent signs and broadcasts through your own RPC, paying the gas.

## First Trade Checklist

1. Register an agent and, for a separate agent, send its `delegationTx` from the master
   wallet ([Wallet & Agent Setup](../authenticated-setup.md)).
2. Send the agent a little ETH for gas.
3. From the master wallet, approve the Diamond to spend the collateral token, once, for at
   least the collateral you will trade (`maxUint256` is common). The addresses come from
   the API (below).
4. Prepare the order with `orders.create`.
5. Sign the returned transaction with the agent key, broadcast it through your RPC before
   it expires, and wait for the receipt.
6. Report the hash with `orders.submit` and keep the `id` it returns.

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  chain = await client.trading.system.chain()
  btc = await client.trading.markets.get('BTC/USD')
  usdc = next(c for c in btc['collaterals'] if c['symbol'] == 'USDC')
  print(chain['diamond'], usdc['address'], usdc['decimals'])  # spender, token, token decimals
```

`client.trading.account.get(trader)` shows each collateral's current `allowance`.

## Sign and Broadcast

The examples below use a `broadcast` function you provide, with web3.py, a wallet SDK or
your own signer. `tx_fields` shows how a `PreparedTransaction` maps to transaction fields:

```python
from datetime import datetime, timezone
from typed_gtrade.trading.schemas import PreparedTransaction

def tx_fields(tx: PreparedTransaction) -> dict[str, str | int]:
  """The prepared transaction's EVM fields; the signer adds the nonce and fees."""
  if datetime.now(timezone.utc) >= tx['expiresAt']:
    raise ValueError('The transaction expired: prepare it again')
  fields: dict[str, str | int] = {
    'to': tx['to'],             # the Diamond
    'data': tx['data'],
    'value': int(tx['value']),  # the string '0'
    'chainId': tx['chainId'],
  }
  if tx['gas'] is not None:     # None: the API could not estimate it, usually an agent without ETH
    fields['gas'] = tx['gas']
  return fields

async def broadcast(key: str, tx: PreparedTransaction) -> str:
  """Send the transaction signed for `key` through your RPC and return its hash once mined.

  The first call signs `tx_fields(tx)` with the agent key and saves the signed transaction
  under `key` before sending it; a retry re-sends the saved one instead of signing again.
  """
  ...
```

`expiresAt` is a deadline, not a transaction field. The signer picks the nonce, so a newly
signed copy of `tx` is a second valid transaction, while a re-sent saved one can be mined
only once.

## Place a Market Order

```python
from typed_gtrade import GTrade
from typed_gtrade.trading.schemas import PreparedTransaction

async def broadcast(key: str, tx: PreparedTransaction) -> str:
  """Sign `tx` once with the agent key, save it under `key`, send it, return the hash once mined."""
  ...

async with GTrade.new(timeout=30) as client:
  prepared = await client.trading.orders.create({
    'market': 'BTC/USD', 'side': 'long', 'type': 'market',
    'size': '0.001', 'leverage': '10', 'collateral': 'USDC',
    'slippage': '0.5', 'clientId': 'my-order-1',
  })
  order, tx = prepared['order'], prepared['transaction']
  if order['status'] == 'prepared' and order['txHash'] is None and tx is not None:
    tx_hash = await broadcast('my-order-1', tx)
    order = await client.trading.orders.submit(id=order['id'], tx_hash=tx_hash)
  order_id = order['id']  # the order's id from now on
  print(order_id, order['status'])
```

`size` is in the base asset, `slippage` in percent (default 1), and decimals can be passed
as `str` or `Decimal`, within the market's `sizePrecision` and `pricePrecision`. `sl`, `tp`
and `reduceOnly` are optional. Writes are the slowest calls, hence `timeout=30` (seconds,
default 5).

The id `orders.create` returns is a prediction: if the chain assigns another, the order is
re-keyed when the transaction lands. Use the id `submit` returns once the receipt exists.

## Retry Safely

`clientId` deduplicates preparing, not broadcasting: re-sending an order with the same
`clientId` returns the existing order, but the API cannot know whether you already sent its
transaction, and a newly signed copy places the order twice. On a retry:

1. Broadcast only while the order is `prepared` with no `txHash`, as above. `txHash` is
   set by `submit`, or once the API sees the transaction land.
2. Before that, only your records know: re-send the saved signed transaction, never a new
   one. If you saved none, check whether the agent's on-chain nonce moved since the first
   attempt before signing again.

`orders.update`, `orders.cancel`, `positions.close` and `positions.update` take no
`clientId`: each call prepares a new transaction. Before repeating one, check the result
of the first with `orders.get`, `account.orders` or `account.positions`: a partial close
or collateral change sent twice applies twice.

## Place a Limit or Stop Order

```python
from typed_gtrade import GTrade

async with GTrade.new() as client:
  prepared = await client.trading.orders.create({
    'market': 'ETH/USD', 'side': 'long', 'type': 'limit',
    'size': '0.5', 'price': '2500', 'leverage': '5', 'sl': '2300', 'tp': '3000',
  })
```

`price` is required for `limit` and `stop`: a `limit` long triggers when the price falls to
it, a `stop` long when it rises to it (the reverse for shorts). Broadcast and submit it as
above; the order rests on-chain as `open` once mined.

## Track an Order

```python
from typed_gtrade import GTrade

order_id = '123456'  # the id orders.submit returned

async with GTrade.new() as client:
  order = await client.trading.orders.get(order_id)
  if order['status'] == 'filled' and order['fill'] is not None:
    print(order['fill']['price'], order['fill']['positionId'])
  elif order['status'] == 'rejected':
    print(order['reason'])  # 'SLIPPAGE', 'EXPOSURE_LIMITS', ...
```

Statuses run `prepared`, then `pending` (market) or `open` (limit/stop), then `filled`,
`rejected`, `timed_out` or `canceled`; a prepared order never broadcast becomes `expired`.
A rejection after broadcast is a status with a `reason`, not an exception. If `submit`
answered before the receipt (status still `prepared`), find the order later by its `txHash`
in `account.orders(trader)` or `account.order_history(...)`. The `orders` channel in
[Listen To Live Streams](listen-to-live-streams.md) pushes every transition.

## Update or Cancel an Order

```python
from typed_gtrade import GTrade

order_id = '123456'  # a resting limit or stop order

async with GTrade.new() as client:
  updated = await client.trading.orders.update(order_id, price='2450', tp='3100')
  canceled = await client.trading.orders.cancel(order_id)
  if canceled['transaction'] is not None:
    ...  # broadcast it, as above
```

Both return a transaction to broadcast; the order follows the chain from there, with no
`submit`. `update` changes a resting order's price, stop loss, take profit or slippage; to
change its size, cancel it and create a new one. `cancel` cancels a resting order, or
withdraws a prepared order never broadcast (`transaction` is `None`); it cannot recall a
transaction you already sent.

### Reclaim a Timed-Out Market Order

A `pending` market order cannot be canceled. If the oracle never fills it, its collateral
stays locked until you broadcast the reclaim transaction yourself. Once the timeout passes
(about a minute), `cancel` returns that transaction:

```python
from typed_gtrade import BadRequest, GTrade

order_id = '123456'  # a market order still pending

async with GTrade.new() as client:
  try:
    reclaim = await client.trading.orders.cancel(order_id)
    if reclaim['transaction'] is not None:
      ...  # broadcast it, as above
  except BadRequest as e:
    if e.args[0] == 'ORDER_NOT_MODIFIABLE':  # too early
      print(e.args[2].get('details', {}).get('reclaimableAtBlock'))  # retry from this block
```

## Close or Update a Position

```python
from typed_gtrade import GTrade

async with GTrade.new() as client:
  partial = await client.trading.positions.close('987654', size='0.0005', slippage='0.5')
  sl_tp = await client.trading.positions.update('987654', sl='60000', tp='80000')
  margin = await client.trading.positions.update('987654', collateral={'action': 'add', 'amount': '50'})
  print(partial['order']['id'], sl_tp['position']['leverage'], margin['transaction']['to'])
```

`close` returns a close order, for `size` of the position or, without it, all of it:
broadcast and submit it like a create, with the same guard. `update` also changes
`leverage`; broadcast its transaction, with no `submit`.

See the upstream [orders guide](https://docs.gains.trade/developer/trading-api/orders).
