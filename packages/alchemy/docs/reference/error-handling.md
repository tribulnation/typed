# Error Handling

`typed_alchemy` maps every failure to a `typed_core` exception, re-exported at the package
root:

- `AuthError`: missing `ALCHEMY_API_KEY`, or an HTTP 401/403 (also raised for a JSON-RPC
  error whose code or message indicates an auth failure)
- `RateLimited`: HTTP 429, or a JSON-RPC error whose code or message indicates rate
  limiting
- `BadRequest`: any other HTTP 4xx, or a JSON-RPC parse/invalid-request/method/params error
- `ApiError`: HTTP 5xx or any other unsuccessful response, or any other JSON-RPC error
- `ValidationError`: the response didn't match the expected schema
- `NetworkError`: connection failures, timeouts, transport errors
- `LogicError`: a local client-side logic error, unrelated to the network

## Recommended Pattern

```python
from typed_alchemy import (
  Alchemy,
  ApiError,
  AuthError,
  BadRequest,
  NetworkError,
  RateLimited,
  ValidationError,
)

async with Alchemy.new() as client:
  try:
    balances = await client.token(network='ethereum').get_token_balances(address='0x...')
  except AuthError:
    ...
  except RateLimited:
    ...
  except BadRequest:
    ...
  except ValidationError:
    ...
  except ApiError:
    ...
  except NetworkError:
    ...
```

## Operational Guidance

- retry transient network failures carefully
- do not blindly retry authentication failures — check `ALCHEMY_API_KEY` first
- log validation failures because they often signal an upstream Alchemy API change
