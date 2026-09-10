# Error Handling

The client distinguishes between failure modes through explicit exception types.

## Common Error Categories

- `NetworkError`: connection failures, timeouts, and transport errors
- `AuthError`: authentication or signing failures
- `RateLimited`: HTTP 429 from either the info or exchange endpoint; a subclass of
  `ApiError`, with the status and response text preserved
- `ApiError`: the remote API returned an application-level error
- `ValidationError`: the response shape did not match the expected schema
- `LogicError`: incorrect local usage of the client, or a `*_paged` sweep that could not
  continue without losing entries

## Pagination

Hyperliquid pages history by time, and its millisecond timestamps are not unique.
Each `*_paged` helper walks forward by moving `start_time` to the latest `time` of every
page that came back full, and stops on the first shorter page. It re-reads the
millisecond a page ends on and drops the rows it already returned by content, so entries
sharing a timestamp are never skipped or duplicated at a page boundary.

Two situations cannot be walked through safely, and the helpers raise `LogicError`
rather than guessing: a millisecond holding a whole page of entries (the endpoint has no
cursor finer than time, so the rest of it is unreachable), and a row returned on one
page that the venue no longer returns when the boundary millisecond is re-read:

```python
from datetime import datetime, timezone
from typed_hyperliquid import Hyperliquid, LogicError

user = '0xYourAccountAddress'
start_time = datetime.fromtimestamp(0, tz=timezone.utc)

async with Hyperliquid.new(public=True) as client:
  try:
    async for page in client.info.user_fills_by_time_paged(user=user, start_time=start_time):
      ...
  except LogicError:
    # the sweep stopped rather than dropping entries; the message names the
    # timestamp it was reading from
    ...
```

Each helper returns a `PaginatedResponse`: `await` it for every entry in one list, or
`async for` it to handle one page at a time, as above. It stops on its own, so there is
nothing to cap; `break` out of the loop to stop early.

## Recommended Pattern

```python
from typed_hyperliquid import ApiError, AuthError, NetworkError, ValidationError

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
