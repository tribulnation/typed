# Error Handling

Typed Clients should distinguish between failure modes clearly.

## Common Error Categories

- `NetworkError`: connection failures, timeouts, transport errors
- `AuthError`: missing credentials, invalid signatures, rejected authentication
- `BadRequest`: invalid request parameters or malformed payloads rejected locally or remotely
- `RateLimited`: provider-side rate limiting
- `ApiError`: the remote API returned an application-level error
- `ValidationError`: the response shape did not match the expected schema
- `LogicError`: incorrect local usage of the client

## Recommended Pattern

```python
from dydx.core import ApiError, AuthError, NetworkError, RateLimited, ValidationError

try:
  ...
except ValidationError:
  ...
except AuthError:
  ...
except RateLimited:
  ...
except ApiError:
  ...
except NetworkError:
  ...
```

## Operational Guidance

- retry transient network failures carefully
- do not blindly retry authentication failures
- back off on rate limits according to the provider's documented policy
- log validation failures because they often signal upstream API changes
- include request identifiers from the provider when available
