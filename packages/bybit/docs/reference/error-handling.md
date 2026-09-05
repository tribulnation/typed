# Error Handling

## The v5 Envelope

Every Bybit v5 REST response is wrapped:

```json
{"retCode": 0, "retMsg": "OK", "result": {...}, "retExtInfo": {}, "time": 1785337186988}
```

The important part: **an application error still arrives with HTTP status 200.** A request for a
nonexistent symbol is a perfectly successful HTTP exchange carrying `retCode: 10001`. Code that
only checks the status code would treat it as a valid empty result.

Typed Bybit does not hand you the envelope. `bybit.core.envelope.unwrap` inspects `retCode`,
raises when it is non-zero, and returns `result` when it is zero — so an endpoint method either
returns a validated payload or raises. There is no success-shaped failure.

That is also why response types describe `result` only. `KlineResult` is the contents of
`result`, not the envelope around it.

## Mapping

Two mappings apply, in order.

**Non-2xx HTTP status**, before the body is even parsed:

| Status | Exception |
| --- | --- |
| `401`, `403` | `AuthError` |
| `429` | `RateLimited` |
| any other `4xx` | `BadRequest` |
| anything else unsuccessful | `ApiError` |

**Non-zero `retCode`**, on an otherwise successful response:

| `retCode` | Exception | Meaning |
| --- | --- | --- |
| `10003`, `10004`, `10005`, `10010`, `10016`, `33004` | `AuthError` | key, signature, permission, or IP rejected |
| `10006`, `10018`, `10429`, `20003` | `RateLimited` | request throttled |
| `10001`, `10002`, `10009`, `20006` | `BadRequest` | malformed request parameters |
| anything else non-zero | `ApiError` | any other application error |

`AuthError` also covers a client built without credentials calling a signed endpoint
(`client.account`, `client.private`, `client.trade_ws`) — see
[API Keys Setup](../api-keys.md).

Each exception carries the code, the message, and the full envelope, in that order:

```python
from typed_bybit import Bybit, BadRequest

async with Bybit.new(public=True) as client:
  try:
    await client.market.tickers(category='spot', symbol='NOTREAL')
  except BadRequest as e:
    code, message, payload = e.args
    print(code, message)
    print(payload['retCode'], payload['retMsg'])
```

That prints `10001 Not supported symbols` — a live, reproducible example of the whole path.

## Two More Failure Modes

`ValidationError` is raised when the body is not JSON, is not a v5 envelope, or when `result`
does not match the expected schema. Since responses are validated by default, this is how you
learn that Bybit changed a field.

`NetworkError` comes from the transport layer: connection failures, timeouts, DNS.

## Exception Hierarchy

All of these come from `typed-core` and are re-exported from the package root, so importing from
`bybit` is enough:

```python
from typed_bybit import Error, NetworkError, ValidationError, ApiError, BadRequest, AuthError, RateLimited, LogicError
```

- `Error` — base of everything below
- `NetworkError` — transport failure
- `ValidationError` — response did not match the expected shape
- `ApiError` — application-level error returned by Bybit
    - `BadRequest` — invalid request parameters
    - `AuthError` — credential, signature, permission, or IP rejection
    - `RateLimited` — throttled
- `LogicError` — incorrect local usage of the client

## Recommended Pattern

Order matters — catch the specific subclasses before `ApiError`:

```python
from typed_bybit import Bybit, ApiError, BadRequest, NetworkError, RateLimited, ValidationError

async with Bybit.new(public=True) as client:
  try:
    ticker = await client.market.tickers(category='spot', symbol='BTCUSDT')
  except BadRequest:
    ...
  except RateLimited:
    ...
  except ApiError:
    ...
  except ValidationError:
    ...
  except NetworkError:
    ...
```

## Operational Guidance

- Public market endpoints share **600 requests per 5 seconds per IP**. The client does not
  throttle for you; back off when you see `RateLimited`.
- Retry transient `NetworkError` failures with backoff. Every endpoint here is a read, so retries
  are safe.
- Do not blindly retry `BadRequest`. The parameters will still be wrong next time.
- Log `ValidationError` loudly. It usually means the upstream schema moved, and silently
  disabling validation would hide a real change.
- `validate=False`, per client or per call, turns off validation but **not** envelope handling.
  `retCode` is still checked and still raises.
