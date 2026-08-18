# API Keys Setup

Most of Typed Bybit needs no credentials at all: the v5 Market REST surface
(`client.http.market`) and the six public-category WebSocket streams (`client.ws.spot`,
`.linear`, `.inverse`, `.option`, `.spread`, `.rfq`) are open to anyone. Credentials are only
needed for `client.http.account`, `client.ws.private`, and `client.ws.trade`.

## Environment Variables

```bash
# .env
BYBIT_API_KEY="your_api_key"
BYBIT_API_SECRET="your_api_secret"
```

## Constructing A Client

```python
from bybit import Bybit

async with Bybit.new() as client:  # reads BYBIT_API_KEY / BYBIT_API_SECRET
  balance = await client.http.account.wallet_balance(accountType='UNIFIED')
  print(balance['list'][0]['accountType'], balance['list'][0]['coin'])
```

Or pass credentials directly instead of relying on the environment:

```python
from bybit import Bybit

async with Bybit.new(api_key='...', api_secret='...') as client:
  ...
```

`Bybit.new()` is authenticated by default — it raises `AuthError` if neither the environment
nor the constructor supplies a key and secret. Pass `public=True` for the credential-free
client, restricted to `client.http.market` and the public WebSocket streams:

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  ticker = await client.http.market.tickers(category='spot', symbol='BTCUSDT')
```

One key/secret pair authenticates every transport on the client: signed HTTP requests
(`client.http.account`), the signed `private` WebSocket connection (`client.ws.private`), and
the signed WS Trade order-entry connection (`client.ws.trade`).

See [Configuration](reference/configuration.md) for `region`, `testnet`, and the rest of the
constructor's arguments.
