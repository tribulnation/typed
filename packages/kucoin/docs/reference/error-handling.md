# Error Handling

Every exception is importable from `kucoin` directly:

```python
from typed_kucoin import ApiError, AuthError, BadRequest, NetworkError, RateLimited, ValidationError

try:
  ...
except ValidationError:
  ...  # response shape didn't match the expected schema
except AuthError:
  ...  # missing, invalid, or rejected credentials
except RateLimited:
  ...  # rate limited, HTTP 429 or code 429000
except BadRequest:
  ...  # invalid parameters, rejected order, or bad content type
except ApiError:
  ...  # any other application-level failure KuCoin returned
except NetworkError:
  ...  # connection failure, timeout, or transport error
```

## KuCoin's Response Envelope

Every REST response carries `{"code": ..., "data": ..., "msg": ...}`. `code == "200000"`
means success; the client raises on any other code and returns `data` directly, so a
successful call never needs to unwrap the envelope itself.

## Known Error Codes

| Code | Meaning | Raised as |
|---|---|---|
| `400001` | Missing key, timestamp, passphrase, or version header | `AuthError` |
| `400002` | Timestamp more than 5 seconds off the server clock | `AuthError` |
| `400003` | API key does not exist | `AuthError` |
| `400004` | Invalid passphrase | `AuthError` |
| `400005` | Signature error | `AuthError` |
| `400006` | Requesting IP not in the key's whitelist | `AuthError` |
| `400007` | Access denied | `AuthError` |
| `411100` | Account frozen | `AuthError` |
| `400100` | Parameter error | `BadRequest` |
| `400200` | Order rejected | `BadRequest` |
| `415000` | Unsupported content type | `BadRequest` |
| `429000` | Rate limited | `RateLimited` |

Any other code raises `ApiError`. When a response isn't a decodable envelope at all, the
HTTP status decides: `401`/`403` → `AuthError`, `429` → `RateLimited`, other `4xx` →
`BadRequest`, everything else → `ApiError`.

## Missing Credentials

`AuthError` is also raised locally, before any request is sent: building a client with
`KuCoin.new()` and no key/secret/passphrase available, or calling an authenticated
method or private WebSocket topic on a client built with `public=True`.
