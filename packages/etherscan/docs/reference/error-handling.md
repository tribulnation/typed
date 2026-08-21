# Error Handling

`typed_etherscan` raises the shared `typed_core` exception hierarchy, re-exported from the
top-level package — no venue-specific exception classes.

```python
from typed_etherscan import ApiError, AuthError, Etherscan, NetworkError, ValidationError

async with Etherscan.new() as client:
  try:
    balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
  except AuthError:
    ...   # no API key, or the client was built with public=True
  except ApiError:
    ...   # Etherscan returned status="0" -- bad address, PRO-tier gate, rate limit, etc.
  except ValidationError:
    ...   # the response didn't match the expected shape
  except NetworkError:
    ...   # connection failure, timeout
```

- `AuthError` — no credentials resolved, or an authenticated method was called on a client
  built with `public=True`.
- `ApiError` — Etherscan's own envelope reported `status: '0'`. This is also what a
  paid-tier-gated endpoint raises on the free tier (`message` names it, e.g. "...API Pro
  endpoint...").
- `RateLimited` — Etherscan's own rate limit was hit; set `ETHERSCAN_RATE_LIMIT` (see
  [Environment Variables](env-vars.md)) to cap calls client-side and avoid this reactively.
- `ValidationError` — the response didn't match the generated response type.
- `NetworkError` — a transport-level failure (timeout, connection error).
