# Error Handling

The client distinguishes between failure modes through explicit exception types.

## Common Error Categories

- `NetworkError`: connection failures, timeouts, and transport errors
- `AuthError`: authentication or signing failures
- `ApiError`: the remote API returned an application-level error
- `ValidationError`: the response shape did not match the expected schema
- `LogicError`: incorrect local usage of the client, or a `*_paged` sweep that could not
  continue without losing entries

## Pagination

Hyperliquid pages history by time, and its millisecond timestamps are not unique.
The `*_paged` helpers therefore re-read the millisecond a page ends on and drop the
overlap by position, so entries sharing a timestamp are never skipped at a page
boundary.

A millisecond holding a whole page of entries cannot be read past, because the
endpoint has no cursor finer than time. The helpers raise `LogicError` rather
than skipping it:

```python
from hyperliquid import Hyperliquid, LogicError

user = '0xYourAccountAddress'
start_ms = 0

async with Hyperliquid.http(public=True) as client:
  try:
    async for page in client.info.user_fills_by_time_paged(user=user, start_time=start_ms):
      ...
  except LogicError:
    # the sweep stopped rather than dropping entries; the message names the
    # timestamp to resume from if the loss is acceptable
    ...
```

## Recommended Pattern

```python
from hyperliquid import ApiError, AuthError, NetworkError, ValidationError

try:
  ...
except ValidationError:
  ...
except AuthError:
  ...
except ApiError:
  ...
except NetworkError:
  ...
```

## Operational Guidance

- retry transient network failures carefully
- do not blindly retry signing or authentication failures
- log validation failures because they often signal upstream API changes
- keep trading examples separate from harmless exchange actions like `noop()`
