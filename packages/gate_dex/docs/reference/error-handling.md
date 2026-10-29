# Error Handling

Every exception derives from `typed_gate_dex.Error` and is importable from the package root.
Gate answers each request with a numeric `code`; the client maps it to an exception, and the
code wins over the HTTP status whenever the response carries one.

| Exception | Raised when |
| --- | --- |
| `AuthError` | no credentials passed or found when building the client; a rejected key, signature, timestamp, request id or IP (codes `10001`-`10003`, `10005`, `10008`, `10101`-`10103`, `10111`-`10113`, `10121`, `10122`, `10161`); HTTP `401`/`403` |
| `RateLimited` | Gate's global, per-key or per-action limit (codes `10131`-`10133`); HTTP `429` |
| `BadRequest` | the request itself is wrong: missing or mistyped parameters (`10004`, `20001`, `20002`, `20009`, `31801`, `41001`), an unsupported chain, token or candle period (`20005`, `21001`, `41003`, `31108`, `31112`), a token not found (`41102`), too many candles (`21003`), a swap amount out of range (`31101`, `31102`, `31106`, `31107`); any other HTTP `4xx` |
| `ApiError` | any other code: no route or not enough liquidity, too much price impact, gas above the output, a failed build simulation (`31500`), an expired order or a signed transaction that failed verification (`31601`), an order not found (`31701`), an error relayed from Gate's quote service (`31000`); HTTP `5xx` |
| `NetworkError` | the connection failed or timed out |
| `ValidationError` | a response did not match its declared type, or was not a Gate response at all |
| `LogicError` | a paginated walk cannot go on without skipping rows: `candles_paged` raises it when Gate returns a full page of candles that all share one timestamp, which is what `limit=1` gets, since Gate's `end` bound is inclusive. Use a `limit` of at least 2 |

`AuthError`, `RateLimited` and `BadRequest` are subclasses of `ApiError`, so catch them
first. A venue error carries `(code, message, response)` as its `args`; an HTTP failure
without a Gate response body carries `(status, body)`.

```python
from typed_gate_dex import ApiError, AuthError, BadRequest, GateDex, RateLimited

async with GateDex.new() as client:
  try:
    quote = await client.trade.quote(
      chain_id=1,
      amount_in='0.01',
      token_in='-',
      token_out='0xdac17f958d2ee523a2206206994597c13d831ec7',
      slippage=0.01,
      slippage_type=1,
      user_wallet='0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    )
  except AuthError as e:
    print('check the key, its IP allowlist and the clock:', e.args)
  except RateLimited:
    print('slow down')
  except BadRequest as e:
    print('rejected:', e.args)
  except ApiError as e:
    print('no quote:', e.args)
```

## Failed Swaps

A swap that fails on chain is not an exception. `client.trade.status(...)` returns its order
with a non-zero `error_code` and an `error_msg` (Gate's agent skills cite `50005` for a
malformed signed transaction, for instance).

## Validation

Responses are validated by default. A `ValidationError` means Gate sent something the types
do not describe. Pass `validate=False` to one call, or to `GateDex.new(...)`, to get the raw
payload back instead.
