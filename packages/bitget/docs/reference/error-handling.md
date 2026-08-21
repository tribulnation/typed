# Error Handling

```python
from typed_bitget import Bitget
from typed_bitget.core.exc import ApiError, AuthError, BadRequest, NetworkError, RateLimited, ValidationError

async with Bitget.new() as client:
  try:
    await client.uta.account.assets()
  except AuthError:
    ...  # missing/invalid credentials, or a signature Bitget rejected
  except RateLimited:
    ...  # HTTP 429, or embedded code 1001 ("request too frequent")
  except BadRequest:
    ...  # invalid parameters, rejected locally or by Bitget
  except ApiError:
    ...  # any other non-"00000" Bitget response code
  except ValidationError:
    ...  # the response didn't match the client's expected shape
  except NetworkError:
    ...  # connection failure, timeout, transport error
```

## How Bitget Errors Map

Every REST response is `{"code": "00000", "msg": "success", "data": ...}` on success. HTTP
status stays `200` on most application-level errors, so the client checks both the HTTP status
and the embedded `code`:

| Signal | Exception |
|---|---|
| HTTP 401 / 403 | `AuthError` |
| HTTP 429 | `RateLimited` |
| HTTP 4xx (other) | `BadRequest` |
| HTTP 5xx / other unsuccessful | `ApiError` |
| code `40001`–`40003`, `40005`, `40006`, `40008`–`40012`, `40014`, `40016`, `40018`, `40037` | `AuthError` |
| code `1001` | `RateLimited` |
| code `40017`, `40019`, `40034`, `400172`, `40707`, `40709` | `BadRequest` |
| any other non-`"00000"` code | `ApiError` |

## Operational Guidance

- retry transient network failures; don't blindly retry auth failures
- back off on `RateLimited`; Bitget documents per-endpoint rate limits
- `ValidationError` usually signals an upstream Bitget response-shape change; log it
