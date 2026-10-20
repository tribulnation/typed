# Error Handling

Exceptions are importable from `typed_grvt`.

| Exception | When |
| --- | --- |
| `AuthError` | GRVT codes `1000`, `1008` (HTTP `401`) and `1001`, `1400`, `2000`-`2008`, `2091`, `2141`, `4015`, `4016`, `7701` (HTTP `403`); a JSON `401`/`403` from the edge host; and, before sending, missing credentials, a malformed private key, an authenticated call on a `public=True` client, a signed call without a private key, or a trading call that leaves `sub_account_id` out when the client has no default trading sub-account (see [Environment Variables](env-vars.md)) |
| `RateLimited` | HTTP `429` or GRVT code `1006` |
| `BadRequest` | any other `4xx`: every GRVT code not listed in this table, such as most order validation codes (`2020`, `2021`, `2064`, ...) and not found (`1004`); max open orders (`2090`), which GRVT sends as a `429` but waiting does not clear; and the requests the client refuses before sending (see [Checked Before Sending](#checked-before-sending)) |
| `ApiError` | GRVT server errors: codes `1002`, `1005`, `3004`-`3006`, `7100`, `7103` (HTTP `500`), `1009`, `1015` (`503`), `1014` (`504`), or any other `5xx`; and a non-JSON `401`/`403`, such as a Cloudflare challenge page (`Blocked by ...`) |
| `NetworkError` | connection failures, timeouts, a dropped WebSocket, a gap or decrease in a stream's sequence |
| `ValidationError` | a reply or stream message that does not match its type, or a stream message with no sequence number |
| `LogicError` | a page walk that cannot go on without skipping rows: `candlesticks_paged` receiving a full page of candles that all share one `open_time` |

Over HTTP the exception follows the status GRVT sends; over WebSocket, where errors carry no
status, it follows the status GRVT's own code table gives each code (the one listed above).
`AuthError`, `RateLimited` and `BadRequest` subclass `ApiError`; every exception subclasses
`Error`.

## Checked Before Sending

The client raises `BadRequest` without contacting GRVT for:

1. a request that does not match its type: a missing required field, a value of the wrong
   type (a `float` or `int` where a decimal takes a `Decimal` or a `str`), or a field the
   request does not declare;
2. in a payload the client signs, a value the signature cannot encode exactly: a limit price
   with more than 9 decimals (GRVT's fixed price precision), an order size with more decimals
   than the instrument's `base_decimals`, a transfer or withdrawal amount with more decimals
   than the currency's `balance_decimals`, a decimal string not in plain notation (`'4E-3'`),
   a negative or oversized value, an unknown `time_in_force` or currency, or a malformed
   address or sub-account id;
3. a stream subscription that would replace or repeat a live one (see
   [Listen To Live Streams](../how-to/listen-to-live-streams.md)).

The client does not check an order against the instrument's trading rules. GRVT does, after
the order is sent, and its refusals are raised as `BadRequest` too: a price off the
`tick_size` grid (`2064`), a size below `min_size` (`2062`) or too granular (`2065`), and a
notional below `min_notional` (`2066`).

## Error Details

`e.args` takes one of two shapes:

1. `(code, message, ...)` when the error carries a code, such as GRVT's numeric error code,
   an edge host `err_...` code, or an HTTP status. Anything after `message` is there for
   debugging.
2. A single message string otherwise, as for the errors the client raises before sending.

So read `code` and `message` only when there are at least two arguments:

```python
from typed_grvt import Grvt
from typed_grvt import (
  ApiError,
  AuthError,
  BadRequest,
  NetworkError,
  RateLimited,
  ValidationError,
)

async with Grvt.new(env='testnet') as client:
  try:
    await client.trading.order({'client_order_id': '9300000000000000001'})
  except AuthError as e:
    print('check credentials or permissions:', e.args)
  except RateLimited:
    print('slow down')
  except BadRequest as e:
    if len(e.args) >= 2:
      code, message = e.args[0], e.args[1]
      print('rejected with code', code, message)
    else:
      print('rejected:', e)
  except ApiError as e:
    print('GRVT failed:', e)
  except NetworkError as e:
    print('network:', e)
  except ValidationError as e:
    print('unexpected reply shape:', e)
```

## Operational Guidance

1. Retry `NetworkError` carefully: a write may have reached GRVT before the connection
   dropped. Check by `client_order_id` before resending an order.
2. Do not retry `AuthError` blindly: an expired session is already renewed and retried once
   for you.
3. Back off on `RateLimited`; GRVT sends no retry-after hint.
4. An `ApiError` reading `Blocked by ...` comes from a proxy in front of GRVT, not from GRVT:
   logging in again does not help.
5. Log `ValidationError`s: they usually mean GRVT changed a reply. Pass `validate=False` to
   a call (or `Grvt.new(validate=False)`) to receive the raw reply meanwhile.
6. After a stream ends with `NetworkError` or `ValidationError`, subscribe again.
