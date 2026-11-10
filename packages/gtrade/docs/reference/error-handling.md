# Error Handling

Every surface raises the same exceptions, importable from `typed_gtrade`:

| Exception | Raised when |
| - | - |
| `NetworkError` | The connection failed or timed out, or a WebSocket dropped mid-stream |
| `ValidationError` | A response or frame did not match its expected shape |
| `ApiError` | The API failed server-side (base class of the three below) |
| `BadRequest` | The API rejected the request itself |
| `AuthError` | Credentials, signature, delegation or agent scope were rejected, or are missing |
| `RateLimited` | The request was throttled |
| `LogicError` | The client was used incorrectly |

All of them derive from `Error`.

## Recommended Pattern

```python
from typed_gtrade import ApiError, AuthError, BadRequest, GTrade, NetworkError, RateLimited, ValidationError

async with GTrade.new() as client:
  try:
    prepared = await client.trading.orders.create({
      'market': 'BTC/USD', 'side': 'long', 'type': 'market', 'size': '0.001', 'leverage': '10',
    })
  except AuthError as e:
    print('credential or scope rejected:', e)
  except RateLimited as e:
    delay = e.args[-1]  # seconds the API asks to wait, or None
  except BadRequest as e:
    code = e.args[0]  # 'SIMULATION_REVERTED', 'SIZE_BELOW_MINIMUM', ...
  except ApiError:
    ...  # server-side failure
  except (NetworkError, ValidationError):
    ...
```

## Trading API Errors

A Trading API error carries `(code, message, error)` as its `args`: the documented error
code, its message, and the whole error object, `details` included. The same codes arrive on
the WebSocket. A `RateLimited` adds one last argument, the `Retry-After` delay (see
[Rate Limits](#rate-limits)).

| Exception | Codes |
| - | - |
| `AuthError` | `UNAUTHENTICATED`, `INVALID_SIGNATURE`, `TIMESTAMP_OUT_OF_WINDOW`, `NONCE_REUSED`, `AGENT_UNKNOWN`, `API_KEY_UNKNOWN`, `AGENT_NOT_DELEGATED`, `AGENT_EXPIRED`, `AGENT_REVOKED`, `SCOPE_READ_ONLY`, `SCOPE_MARKET_NOT_ALLOWED`, `SCOPE_LEVERAGE_EXCEEDED`, `SCOPE_SPEND_CAP_EXCEEDED`, `TRADER_MISMATCH`, `TRADER_NOT_IN_BETA` |
| `RateLimited` | `RATE_LIMITED` |
| `BadRequest` | `VALIDATION_ERROR`, `CHAIN_NOT_FOUND`, `CHAIN_READ_ONLY`, `MARKET_NOT_FOUND`, `ORDER_NOT_FOUND`, `POSITION_NOT_FOUND`, `AGENT_NOT_FOUND`, `NOT_FOUND`, `IDEMPOTENCY_CONFLICT`, `ORDER_NOT_MODIFIABLE`, `PRECISION_ERROR`, `LEVERAGE_OUT_OF_RANGE`, `SIZE_BELOW_MINIMUM`, `MARKET_CLOSED`, `COLLATERAL_NOT_SUPPORTED`, `SIMULATION_REVERTED`, `SUBMISSION_MISMATCH`, `UNSUPPORTED`, `TOO_MANY_PREPARED_ORDERS` |
| `ApiError` | `INTERNAL`, `UPSTREAM_UNAVAILABLE`, `NOT_READY` |

An unknown code falls back on the HTTP status: 401/403 `AuthError`, 429 `RateLimited`,
other 4XX `BadRequest`, otherwise `ApiError`. Over the WebSocket, where there is no status,
an unknown code raises `ApiError`.

`CHAIN_NOT_FOUND` is what a client built for `base`, `polygon` or `megaeth` gets today from
every `client.trading` REST call except `system.health` and `system.ready`: the Trading API
serves only Arbitrum so far. Its channels on those chains fail to connect, raising
`NetworkError`.

`TRADER_NOT_IN_BETA` appears in the API's published list of error codes without a
description. Its name suggests the trader is not admitted to the Trading API beta; if so,
it concerns the trader rather than the request and retrying will not help. Gains'
documentation does not say how access is granted.

Some details are actionable. `AGENT_NOT_DELEGATED` answers every request the agent signs
while it is not the trader's on-chain delegate, and carries the delegation transaction to
send. Writes are always signed by the agent, reads only when the client has no API key, so
this client is built with `agent` alone:

```python
import os
from typed_gtrade import AuthError, GTrade

trader = '0x...'

async with GTrade.new(agent=os.environ['GTRADE_AGENT_PRIVATE_KEY']) as client:
  try:
    await client.trading.account.positions(trader)
  except AuthError as e:
    if e.args[0] == 'AGENT_NOT_DELEGATED':
      delegation_tx = e.args[2]['details']['delegationTx']  # send from the master wallet
```

`SIMULATION_REVERTED` names the contract error in `details.errorName` and describes the
revert in `details.detail`. A plain revert reason arrives as `errorName` `'Error'`, with the
reason at the end of `detail`. A common one before the first trade is a missing collateral
allowance, `"ERC20: transfer amount exceeds allowance"`: the trader must approve the
Diamond (see the [first trade checklist](../how-to/place-and-manage-orders.md#first-trade-checklist)).

```python
from typed_gtrade import BadRequest, GTrade

async with GTrade.new() as client:
  try:
    await client.trading.orders.create({
      'market': 'BTC/USD', 'side': 'long', 'type': 'market', 'size': '0.001', 'leverage': '10',
    })
  except BadRequest as e:
    detail = e.args[2].get('details', {}).get('detail', '')
    if e.args[0] == 'SIMULATION_REVERTED' and 'exceeds allowance' in detail:
      ...  # approve the Diamond from the master wallet, then prepare the order again
```

A rejection after a transaction is broadcast is not an exception: the order moves to
`rejected` with a `reason` (see [Place & Manage Orders](../how-to/place-and-manage-orders.md)).

## Public Backend Errors

The per-chain backend, Backend Global and pricing raise by HTTP status, with
`(status, message)` as `args` (plus the `Retry-After` delay on a `RateLimited`): 401/403
`AuthError`, 429 `RateLimited`, other 4XX
`BadRequest`, otherwise `ApiError`. An invalid address on the per-chain backend raises
`BadRequest` too.

## Raised Before Any Request

- `GTrade.new()` without `public=True` raises `AuthError` when neither credential is passed
  or set in the environment, or when the agent key is not a valid private key.
- `GTrade.new()` raises `ValueError` for an unknown `chain`, or for `public=True` together
  with `agent` or `api_key`.
- A write on a client with only a read-only API key raises `AuthError` without sending.
- A private Trading API call or channel on a `public=True` client raises `AuthError`.

## Rate Limits

The Trading API documents per-minute windows of 600 requests per IP, 300 per agent or API
key, and 60 writes per agent, plus 200 subscriptions per WebSocket connection. Gains
publishes these as launch values on testnet, with production limits to follow at the
mainnet release.

A throttled request raises `RateLimited`. Its last argument, `e.args[-1]`, is the delay in
seconds from the `Retry-After` header, or `None` when there is none (always, over the
WebSocket). On a Trading API error, `e.args[2]['details']['scope']` says which limit was
hit (`ip`, `agent` or `agent-writes`).

```python
import asyncio
from typed_gtrade import GTrade, RateLimited

async with GTrade.new(public=True) as client:
  try:
    markets = await client.trading.markets.list()
  except RateLimited as e:
    await asyncio.sleep(e.args[-1] or 60)  # the windows are one minute long
    markets = await client.trading.markets.list()
```

## Timeouts

`GTrade.new(timeout=5.0, ws_timeout=10.0)` sets both, in seconds. `timeout` bounds every
HTTP request. Order and position writes are the slowest calls, because the API simulates
the transaction before answering, so raise it if they time out. `ws_timeout` bounds each
WebSocket handshake and the Trading API's reply to every subscribe, unsubscribe and
authentication. Either one running out raises `NetworkError`.

## Operational Guidance

- Retry `RateLimited` (after `e.args[-1]` seconds), `ApiError` (`NOT_READY`,
  `UPSTREAM_UNAVAILABLE`) and `NetworkError` on reads, with backoff.
- Never blindly retry a write that timed out: it may have gone through. A `clientId` on
  `orders.create` makes a retried create return the existing order instead of preparing a
  second one, but it does not protect the broadcast: broadcast only an order still
  `prepared` with no `txHash`, and on a retry re-send the transaction you already signed
  rather than signing it again. The other writes take no `clientId`: check the order or
  position first. See [Retry Safely](../how-to/place-and-manage-orders.md#retry-safely).
- Do not blindly retry `AuthError`.
- A `ValidationError` usually means the API changed shape. Pass `validate=False` to one call,
  or `GTrade.new(validate=False)`, to receive the unvalidated data meanwhile.

See the upstream [errors reference](https://docs.gains.trade/developer/trading-api/errors).
