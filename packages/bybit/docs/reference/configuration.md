# Configuration

Everything is configured through the constructor — see [API Keys Setup](../api-keys.md) for
credentials specifically.

## Constructor

| Argument | Default | Effect |
| --- | --- | --- |
| `api_key` | `None` | Falls back to `BYBIT_API_KEY` |
| `api_secret` | `None` | Falls back to `BYBIT_API_SECRET` |
| `public` | `False` | Build a credential-free client, restricted to `client.market` and the public WebSocket streams |
| `region` | `'global'` | Target a documented regional host — see [Regional Endpoints](#regional-endpoints) |
| `testnet` | `False` | Target that region's testnet host instead of mainnet |
| `base_url` | `None` | Fully-qualified REST base URL override; WebSocket URLs are still resolved from `region`/`testnet` |
| `validate` | `True` | Validate responses against the generated schemas |
| `http` | `None` | Supply your own `HttpClient` instead of a fresh one |

```python
from typed_bybit import Bybit

client = Bybit.new()                                 # authenticated, reads BYBIT_API_KEY/SECRET
client = Bybit.new(public=True)                       # credential-free, market data only
client = Bybit.new(testnet=True)                      # api-testnet.bybit.com
client = Bybit.new(region='eu')                       # api.bybit.eu
client = Bybit.new(validate=False)                    # skip response validation
client = Bybit.new(base_url='http://localhost:8000')  # mock server
```

`Bybit.new()` is authenticated by default and raises `AuthError` if neither the environment
nor the constructor supplies `api_key`/`api_secret`; pass `public=True` for the
credential-free client instead. `region` and `testnet` are independent and freely
combinable — `region` picks the host's domain, `testnet` picks the `api`/`api-testnet`
subdomain on it.

## Regional Endpoints

Bybit operates one REST host per legal entity. `region` selects between them:

| `region` | Mainnet host | Entity |
| --- | --- | --- |
| `'global'` | `https://api.bybit.com` | Global (default) |
| `'bytick'` | `https://api.bytick.com` | Global, alternate domain |
| `'eu'` | `https://api.bybit.eu` | European Economic Area |
| `'nl'` | `https://api.bybit.nl` | Netherlands |
| `'tr'` | `https://api.bybit.tr` | Turkey |
| `'kz'` | `https://api.bybit.kz` | Kazakhstan |
| `'ge'` | `https://api.bybitgeorgia.ge` | Georgia |
| `'ae'` | `https://api.bybit.ae` | United Arab Emirates |
| `'id'` | `https://api.bybit.id` | Indonesia |
| `'jp'` | `https://api.manepa.jp` | Japan |

`testnet=True` swaps `api` for `api-testnet` on the same domain. That host is live for
`global`/`bytick` (`api-testnet.bybit.com`) and `jp` (`api-testnet.manepa.jp`); the other
six regions document no testnet host, so `testnet=True` still builds the same-shaped URL for
them, and it may not resolve to anything.

```python
from typed_bybit import BYBIT_DOMAINS, resolve_rest_base_url

print(resolve_rest_base_url('eu'))       # https://api.bybit.eu
print(BYBIT_DOMAINS['jp'])               # manepa.jp
print(len(BYBIT_DOMAINS))
```

The v5 protocol is identical on every host: same paths, same `{retCode, retMsg, result}`
envelope, same response shapes. Only the **product universe** differs — see
[Regions Do Not Share A Product Universe](#regions-do-not-share-a-product-universe).

Bybit restricts IP addresses located in the US or Mainland China on all of these hosts.

## Regions Do Not Share A Product Universe

!!! warning "A region is not a mirror"
    Each host lists only the products its entity is licensed to offer. Switching region
    silently changes **which symbols exist**, and `region='eu'` lists **no derivatives at
    all** — no linear, no inverse, no options.

Check the product universe for yourself rather than assuming it matches the default host:

```python
from typed_bybit import Bybit

for region in ('global', 'eu'):
  async with Bybit.new(public=True, region=region) as client:
    spot = await client.market.instruments(category='spot')
    print(region, 'spot instruments:', len(spot['list']))
```

Even inside spot the symbol sets differ, so a symbol that resolves globally may not be listed
regionally:

```python
from typed_bybit import Bybit

for region in ('global', 'eu'):
  async with Bybit.new(public=True, region=region) as client:
    info = await client.market.instruments(category='spot', symbol='BTCUSDT')
    print(region, 'BTCUSDT listed:', bool(info['list']))
```

### The Instrument Catalogue Is Not The Queryable Set

`market.instruments` is **not** a reliable inventory of what a regional host will answer for.
On `region='eu'` `BTCUSDT` may be absent from the spot catalogue while `market.tickers` and
`market.kline` still return live `BTCUSDT` data:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True, region='eu') as client:
  listed = await client.market.instruments(category='spot', symbol='BTCUSDT')
  print('BTCUSDT in eu catalogue:', bool(listed['list']))
  ticker = await client.market.tickers(category='spot', symbol='BTCUSDT')
  print('BTCUSDT ticker on eu:', ticker['list'][0]['lastPrice'])
```

So a symbol's absence from `instruments` does not mean market data is unavailable, and its
presence in `tickers` does not mean the entity lists it for trading. If you need the tradable
set, use `market.instruments`; if you need a price, do not gate the call on it.

### How A Missing Product Fails

There is no single failure mode, and **none of them is an obvious "unsupported region"
error**. Against `region='eu'`, asking for derivatives can produce any of:

| Outcome | Endpoints | What you see |
| --- | --- | --- |
| `BadRequest` on `retCode` | `tickers`, `kline`, `orderbook`, `mark_price_kline`, `index_price_kline`, `premium_index_price_kline`, `open_interest`, `funding_history`, `risk_limit`, `long_short_ratio`, `adl_alert` | `retCode` `10001`, `params error: symbol invalid` — the symbol is unknown, not the category |
| `ApiError` on `retCode` | `price_limit` | `retCode` `12814`, `symbol is invalid` |
| `ValidationError` | `instruments` for a derivatives category, `full_orderbook` | HTTP 200, `retCode` 0, but a payload that does not match the schema |
| `BadRequest(404)` | `insurance`, `historical_volatility` | The route does not exist on this host at all |
| Empty list | `delivery_price`, `instruments` for an unlisted spot symbol | HTTP 200, `retCode` 0, `list: []` — indistinguishable from "nothing to report" |

The `ValidationError` cases are the ones worth knowing about. `instruments` on a derivatives
category returns `{"category": "", "list": [], "nextPageCursor": ""}` — an **empty**
`category` string, which is not a member of the `Literal` the schema declares, so validation
rejects it. `full_orderbook` returns `result: {}`, with the `s`, `b`, `a`, `ts` and `u` keys
missing entirely. Neither is an error on the wire; both surface as a schema mismatch.

```python
from typed_bybit import Bybit, ApiError, ValidationError

async with Bybit.new(public=True, region='eu') as client:
  try:
    await client.market.tickers(category='linear', symbol='BTCUSDT')
  except ApiError as e:
    print('tickers(linear):', type(e).__name__, e.args[0])
  try:
    await client.market.instruments(category='linear')
  except ValidationError:
    print('instruments(linear): ValidationError — empty category, not an empty list')
```

Note the last row of the table: with `validate=False` the `instruments` mismatch stops being
an error and becomes an empty list, so **turning validation off turns a loud failure into a
silent one**. That is the opposite of the usual trade-off, and it is the reason to leave
validation on when pointing at a non-global region.

## Base URLs

```python
from typed_bybit import BYBIT_API_URL, resolve_rest_base_url

print(BYBIT_API_URL)                              # https://api.bybit.com
print(resolve_rest_base_url('global', testnet=True))  # https://api-testnet.bybit.com
```

`base_url` takes precedence over both `region` and `testnet` for HTTP, so pointing at a mock
server does not require touching either. There is no matching override for the WebSocket
connections — they always resolve from `region`/`testnet`.

## Connection Pooling

`client.client` is the one shared `HttpTransport`, reused by `client.market`,
`client.account`, and every other REST product domain alike — each is built from that same
transport rather than opening its own. Enter the top-level client as an async context
manager so that one connection pool is reused across every call:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  book = await client.market.orderbook(category='spot', symbol='BTCUSDT', limit=1)
  trades = await client.market.recent_trades(category='spot', symbol='BTCUSDT', limit=1)
  print(book['s'], trades['list'][0]['price'])
```

Calls made outside the context manager still work — the transport opens a connection per
request — but the pool is not reused. See [Async Usage](async-usage.md) for the WebSocket
side of the same picture.

## Validation

`validate=True` is the default. Every endpoint method also accepts a per-call `validate`
override:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  tickers = await client.market.tickers(category='linear', validate=False)
  print(len(tickers['list']))
```

- `validate=None` (the default on each method) follows the client-level setting
- `validate=True` validates this call regardless of the client default
- `validate=False` skips validation for this call

Validation is a pydantic pass over the unwrapped `result`. Turning it off is worth considering
for large responses — `market.tickers(category='linear')` returns several hundred records, and
`market.full_orderbook` ten thousand levels per side — but you lose the early warning when the
upstream schema changes.

Turning validation off does **not** disable envelope handling. `retCode` is still inspected and
still raises. See [Error Handling](error-handling.md).

Response types tolerate undocumented extra fields, so a new Bybit field does not break
validation; a changed or removed one does.

## Raw Requests

For anything not yet covered by a typed method, or to inspect the untouched envelope, use
`client.client` -- the shared `HttpTransport` every generated REST method calls into:

```python
from typed_bybit import Bybit
from typed_bybit.core.envelope import unwrap

async with Bybit.new(public=True) as client:
  r = await client.client.request('GET', '/v5/market/tickers', params={'category': 'spot', 'symbol': 'BTCUSDT'})
  print(r.status_code)
  print(unwrap(r)['list'][0]['lastPrice'])
```

`client.client.request` returns the raw `httpx.Response`. `unwrap(response)` unwraps the
envelope and raises on a non-zero `retCode`, exactly as the generated methods do.
