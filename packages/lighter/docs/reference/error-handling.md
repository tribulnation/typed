# Error Handling

Every exception is importable from `typed_lighter` and derives from `typed_lighter.Error`.

```
Error
├── NetworkError        connection failed, timed out, or dropped
├── ValidationError     a response did not match its declared type
├── LogicError          a client-side invariant was broken
└── ApiError            Lighter answered with an error
    ├── AuthError       missing or rejected credentials
    ├── BadRequest      invalid input, or a refused business rule
    └── RateLimited     throttled
```

## How Lighter Errors Map

Lighter reports failures as a numeric `code` beside a `message`. An error the venue
answered with (from the main API, the explorer or the deposit bridge) carries
`(code_or_status, message, payload)` as its `args`:

- `code_or_status`: Lighter's business code when the venue answered with one, otherwise
  the HTTP status of the failed response. A WebSocket error frame with no numeric code
  carries its raw `code` value here instead: `None` when the frame has none, or the string
  it sent;
- `message`: the venue's explanation;
- `payload`: the full error body as received.

An error raised locally, before anything is sent (the table further down), carries only
`(message,)`, and so do `NetworkError`, `ValidationError` and `LogicError`. Read `args`
by position only after checking its length, or catch by class and use `str(error)`.

Since a business code and an HTTP status are both integers, use `error_code(error)` to tell
them apart: it returns the Lighter business code for a venue business error (also on an
HTTP 5xx whose body carries one), and `None` for an HTTP-status error, a WebSocket error
frame with no numeric code, or anything raised locally.

| Signal | Exception |
|---|---|
| `20013` invalid, expired or foreign auth token; `21108` public key not registered; `21109` API key not found; `21120` invalid signature; `21504` missing Ethereum signature | `AuthError` |
| `21506` too many pending transactions; `23000`–`23004`, `30009`, `30010`; HTTP 429 or 405 | `RateLimited` |
| `20001` invalid parameter (including a missing auth token); `23201`/`23202` testnet faucet refused (portfolio worth 100 USD or more / no faucet on this network); any `211xx`–`224xx` business rule (invalid nonce, order size, margin, ...); WebSocket request errors `30000`–`30003`, `30005`, `30007` | `BadRequest` |
| HTTP 401 with no code | `AuthError` |
| HTTP 403 with no code (the request was blocked before reaching Lighter) | `ApiError` |
| Any other code | `ApiError` |
| Any other HTTP 4xx with no code | `BadRequest` |
| HTTP 5xx, with or without a code | `ApiError` |
| WebSocket error frame with no numeric code | `ApiError` |
| Explorer errors | `RateLimited` (429), `BadRequest` (4xx), `ApiError` (5xx) |
| Deposit bridge errors | `AuthError` (bad key), `RateLimited`, `BadRequest`, `ApiError` |

Raised locally, before anything is sent:

| Situation | Exception |
|---|---|
| No credentials found by `Lighter.new()`, or a malformed API private key | `AuthError` |
| An API key index without its private key, or a private key without its index (arguments or `LIGHTER_API_KEY_INDEX`/`LIGHTER_API_PRIVATE_KEY` with the network's prefix) | `AuthError` |
| API keys with no account index (`account_index=`, or `LIGHTER_ACCOUNT_INDEX` with the network's prefix) | `AuthError` |
| `LIGHTER_ACCOUNT_INDEX` or `LIGHTER_API_KEY_INDEX` (with the network's prefix) set to something that is not an integer | `AuthError` |
| An auth token for a different account than `account_index` | `AuthError` |
| An auth token in an unrecognized format | `AuthError` |
| A transaction, signer call or token-gated call on a client without the credentials it needs (public or read-only) | `AuthError` |
| `change_api_key`, `lit_lease` or `fast_withdraw` on a client with no Ethereum key (the L1 signature is built locally before sending) | `AuthError` |
| A `client.deposit_bridge` call with no bridge API key (`bridge_api_key=`, or `LIGHTER_BRIDGE_API_KEY` with the network's prefix) | `AuthError` |
| An auth token whose expiry is more than 8 hours ahead (`client.signer.auth_token`) | `BadRequest` |
| A `client.explorer` call on a network with no explorer (`robinhood`, `robinhood-testnet`) | `LogicError` |
| The signer rejects a field (out of range, wrong combination), with Lighter's own validation message | `BadRequest` |
| An invalid batch (empty, too long, mixed keys, nonces out of order) | `BadRequest` |

The other L1-signable transactions are not checked locally: without an Ethereum key,
`transfer` and `approve_integrator` are signed and sent with no L1 signature, which is
fine where Lighter does not need one (a transfer between accounts of the same master
account, an approval for an integrator of the same master account or with zero fees).
Where it does, the venue answers `21504`, which is also an `AuthError`.

## Reading The Code

```python
from typed_lighter import ApiError, Lighter, error_code

async with Lighter.new() as client:
  try:
    await client.tx.cancel_order(market_index=0, order_index=999)
  except ApiError as error:
    code = error_code(error)
    if code is not None:
      print('Lighter code', code, error.args[1])
    elif len(error.args) == 3:
      print('HTTP or code-less error', error.args[0], error.args[1])
    else:
      print('Raised locally:', error)
```

## Transactions And Nonces

A transaction Lighter refused with a business code does not burn its nonce: when the
error is a `BadRequest`, `AuthError` or `RateLimited` and `error_code(error)` is a code
other than `21104`, the client reuses the nonce for the next transaction on that key. In
every other case the client refetches the key's nonce from Lighter before its next
transaction: `21104` invalid nonce, any HTTP 5xx (even one whose body carries a code), a
network error, timeout (including a WebSocket transaction with no reply within the
client's 10-second timeout, a `NetworkError`) or cancellation, an error with no business code, a code outside
the classified ranges (a plain `ApiError`), and a reply that fails validation
(`ValidationError`). Except for `21104`, those outcomes are unknown: the transaction may
still have been accepted, so look it up (by `client_order_index`, or by the hash
`client.signer` computes) before sending it again.

The same rules hold however the nonce was chosen: by the client's nonce manager, pinned
with `client.tx.*(nonce=...)`, or signed beforehand and submitted with `client.tx.send` or
`client.tx.batch` (for the client's own account).

A `200` reply means Lighter accepted the transaction, not that it executed; a sequencer
rejection after acceptance raises nothing. Check the account's orders or streams for the
outcome ([Place & Manage Orders](../how-to/place-and-manage-orders.md)).

## Recommended Pattern

```python
from typed_lighter import (
  ApiError,
  AuthError,
  BadRequest,
  Lighter,
  NetworkError,
  RateLimited,
  ValidationError,
)

async with Lighter.new() as client:
  try:
    await client.tx.cancel_all_orders({'mode': 'immediate'})
  except AuthError:
    ...  # fix credentials; do not retry blindly
  except RateLimited:
    ...  # back off, then retry
  except BadRequest:
    ...  # the request itself is wrong; retrying the same call will not help
  except ApiError:
    ...  # other venue errors
  except NetworkError:
    ...  # reads can be retried; streams need resubscribing
  except ValidationError:
    ...  # the response changed shape; log it, or pass validate=False
```

Every API, transaction and stream method takes `validate=False` to skip response validation for one call, and
`Lighter.new(validate=False)` turns it off client-wide.
