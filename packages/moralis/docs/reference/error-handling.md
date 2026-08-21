# Error Handling

Moralis returns a JSON error payload on any non-200 response. The client reads the real
HTTP status code and raises one of `typed_core`'s shared exceptions, all importable
directly from `typed_moralis`.

## Exceptions

| Status code | Exception | Meaning |
| --- | --- | --- |
| 401, 403 | `AuthError` | missing or invalid `MORALIS_API_KEY` |
| 429 | `RateLimited` | Moralis rate limit reached |
| other 4xx | `BadRequest` | invalid request parameters or payload |
| anything else (5xx, ...) | `ApiError` | Moralis returned a server-side error |

`AuthError`, `BadRequest`, and `RateLimited` are all subclasses of `ApiError` -- catch
`ApiError` alone to handle any application-level failure, or catch a specific subclass
first when you need to react differently (refresh credentials on an auth error, back off
and retry on a rate limit).

Two more exceptions can surface from any call and aren't Moralis-specific: `NetworkError`
(connection or timeout failure reaching Moralis) and `ValidationError` (a response that
didn't match its declared shape).

## Error Payload

A Moralis error body carries `message`, and sometimes `code` and/or `details`:

```json
{
  "message": "Invalid chain: not-a-chain",
  "code": "C0005"
}
```

Each raised exception's `args` hold the response's HTTP status code first, then this
payload.

## Example

```python
from typed_moralis import AuthError, BadRequest, Moralis, RateLimited

async with Moralis.new() as client:
  try:
    await client.evm.wallet.history(
      '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
    )
  except AuthError:
    ...  # check MORALIS_API_KEY
  except RateLimited:
    ...  # back off and retry
  except BadRequest as e:
    print(e.args)  # (status_code, payload)
```
