# List Instruments

`market.instruments` returns the trading rules of every instrument in a product category: tick
size, quantity steps, leverage bounds, launch and delivery times.

!!! warning "The listing depends on which host you are on"
    Every example here targets the default global host. A client built with `region=...`
    enumerates a different, usually smaller, universe — `region='eu'` returns no derivatives
    at all, and a derivatives category there fails validation rather than returning an empty
    list. See [Regions Do Not Share A Product
    Universe](../reference/configuration.md#regions-do-not-share-a-product-universe).

## One Symbol

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  info = await client.http.market.instruments(category='spot', symbol='BTCUSDT')
  assert info['category'] == 'spot'
  pair = info['list'][0]
  print(pair['baseCoin'], pair['quoteCoin'], pair['status'])
  print('tick size', pair['priceFilter']['tickSize'])
  print('min order amount', pair['lotSizeFilter']['minOrderAmt'])
```

## The Response Is Discriminated By Category

The return type is a union of three variants, tagged by `category`:

- `SpotInstrumentsInfo` — `category='spot'`, items are `SpotInstrument`, **no** `nextPageCursor`
- `ContractInstrumentsInfo` — `category` is `'linear'` or `'inverse'`, items are `ContractInstrument`
- `OptionInstrumentsInfo` — `category='option'`, items are `OptionInstrument`

The variants do not carry the same fields, so narrow on `category` before reaching into an item.
Type checkers follow the literal:

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  info = await client.http.market.instruments(category='linear', symbol='BTCUSDT')
  if info['category'] == 'spot':
    print(info['list'][0]['marginTrading'])
  elif info['category'] == 'option':
    print(info['list'][0]['symbol'])
  else:
    contract = info['list'][0]
    print(contract['contractType'], contract['settleCoin'])
    print('max leverage', contract['leverageFilter']['maxLeverage'])
```

## Filtering

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  info = await client.http.market.instruments(category='linear', base_coin='BTC', status='Trading')
  print([i['symbol'] for i in info['list']])
```

`status` is one of `'PreLaunch'`, `'Trading'`, `'Delivering'`, `'Closed'`. `base_coin` applies
to linear, inverse, and option only.

## Listing Everything

Spot returns every pair in one response. Linear, inverse, and option are cursor-paginated, with
`limit` up to 1000 and a default of 500:

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  symbols: list[str] = []
  cursor = None
  while True:
    page = await client.http.market.instruments(category='linear', limit=200, cursor=cursor)
    assert page['category'] != 'spot'
    symbols += [i['symbol'] for i in page['list']]
    cursor = page['nextPageCursor']
    if not cursor:
      break
  print(len(symbols))
```

See [Paginate Through Results](paginate-through-results.md) for the general shape of that loop.

## Risk Limit Tiers

Contracts also carry a tiered risk limit table, available separately:

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  tiers = await client.http.market.risk_limit(category='linear', symbol='BTCUSDT')
  for tier in tiers['list'][:3]:
    print(tier['id'], tier['riskLimitValue'], tier['maxLeverage'], tier['maintenanceMargin'])
```

Tiers come ordered from the lowest upwards. `isLowestRisk` is an integer flag, `0` or `1`, not a
boolean.
