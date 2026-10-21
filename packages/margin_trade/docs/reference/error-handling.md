# Error Handling

Every exception the client raises while calling the venue is importable from
`typed_margin_trade` and derives from `Error`. The one exception is a construction mistake:
`MarginTrade.new(wallet, public=True)` (a wallet or `vault` together with `public=True`)
raises a plain `ValueError`.

| Exception | Raised when |
| - | - |
| `NetworkError` | the connection fails or times out, the WebSocket drops, or a subscribe/unsubscribe gets no reply within the client's 10-second timeout (an unanswered subscribe is then unsubscribed, best effort) |
| `ValidationError` | a successful response is not JSON or does not match its schema |
| `AuthError` (an `ApiError`) | the error message contains `Authentication required`, `signature verification failed`, `duplicate signature`, `is not operable by this signer` (an account the signer may not act for) or `timestamp too far from server time`, whatever the HTTP status or response layer; or the status is HTTP 401 or 403; or, locally, a signed call has no wallet or an agent calls a master-only action |
| `RateLimited` (an `ApiError`) | HTTP 429 |
| `BadRequest` (an `ApiError`) | any other HTTP 4xx (its `{"error"}` message), or a soft error inside a successful response (`Unsupported type: ...`, a missing parameter, `invalid network`, `faucet already claimed today`, ...); also a refused WebSocket subscription |
| `ApiError` | any other failed HTTP status (a 5xx), or an `{"status": "err"}` rejection from `/exchange` |
| `LogicError` | a paged walk finds the venue's rows inconsistent between pages |

The auth phrases are checked first: an error carrying one of them is an `AuthError` even
when it arrives with a 4xx or 5xx status, or as a soft error or an `{"status": "err"}`
rejection. Every other error is classified by its HTTP status, then by the layer it came in.

Margin Trade publishes no error codes, so the server's message is the exception's message.

## Per-Order Failures Are Results

`exchange.order`, `modify`, `batch_modify`, `cancel` and `cancel_by_cloid` succeed as a
request even when an individual order fails. Each order's outcome is an entry in
`statuses`, such as `{'error': 'invalid asset index: 9999'}` or `'order not found'`, and is
never raised.

## Raised Before Sending

Some mistakes are caught locally, with nothing sent:

1. A signed call (`exchange`, `solana`, signed `user` calls) on a `public=True` client
   raises `AuthError`.
2. A master-only call (`exchange.approve_agent`, `approve_agent_v2`, `revoke_agent`,
   `get_agents` and `withdraw`) from an agent client raises `AuthError`.
3. `user.faucet_claim()` is testnet-only: on mainnet it raises `BadRequest`.
4. `MarginTrade.new()` without a wallet and without `public=True`, or with a malformed key,
   raises `AuthError`.
5. `MarginTrade.new(wallet, public=True)` (a wallet or `vault` together with `public=True`)
   raises `ValueError`: a client is either public or signed.

## Pattern

```python
import os
from typed_margin_trade import (
  MarginTrade, AuthError, BadRequest, ApiError, NetworkError, ValidationError,
)

async with MarginTrade.new(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'], mainnet=False) as client:
  try:
    profile = await client.user.get_user()
  except AuthError:
    ...  # fix the key, signer or clock; on a `duplicate signature`, check state before retrying an action
  except BadRequest:
    ...  # the request itself is wrong
  except ApiError:
    ...  # server-side failure; retry with backoff
  except NetworkError:
    ...  # transient; a read can be retried, an action may already have applied (see below)
  except ValidationError:
    ...  # the response changed shape; log it
```

## Guidance

1. Signed requests carry a timestamp the server accepts within 60 seconds of its own clock;
   a skewed system clock shows up as `AuthError`.
2. Each signature is single-use: re-sending an identical signed body is refused as
   `duplicate signature`. The client signs every call afresh with a new timestamp, so a
   retry is never refused for reusing the old signature. On an effectful action, though, a
   `duplicate signature` `AuthError` can mean the identical request already reached the
   venue and was applied: check the state first, as for a `NetworkError` (item 3), and
   retry only what did not happen. A read can simply be retried. Other `AuthError`s need a
   fixed key, signer or clock before a retry can succeed.
3. A `NetworkError` on an effectful action (`exchange.order`, `modify`, `cancel`,
   `withdraw`, `usd_class_transfer`, the agent actions, ...) does not mean nothing
   happened: the venue may have applied it before the connection failed. Check the state
   first (`info.open_orders` or `info.order_status` for orders, `info.withdrawal_history`
   for a withdrawal, `info.clearinghouse_state` for a transfer) and retry only what did not
   happen; an order with a client id `c` can be looked up by it.
4. Pass `validate=False` to a call (or to `MarginTrade.new`) to skip response validation,
   for example to inspect a response that fails its schema.
