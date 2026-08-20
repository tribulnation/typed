# API Keys Setup

The v5 Market REST surface (`client.http.market`) and the public-category WebSocket streams
(`client.ws.spot`, `.linear`, `.inverse`, `.option`, `.spread`, `.rfq`, `.finance`) are open
to anyone. Everything else — trading, positions, account and asset data, earn products, and
the `private`/`trade` WebSocket connections — needs credentials.

## Environment Variables

```bash
# .env
BYBIT_API_KEY="your_api_key"
BYBIT_API_SECRET="your_api_secret"
```

## Constructing A Client

```python
from typed_bybit import Bybit

async with Bybit.new() as client:  # reads BYBIT_API_KEY / BYBIT_API_SECRET
  balance = await client.http.account.wallet_balance(account_type='UNIFIED')
  print(balance['list'][0]['accountType'], balance['list'][0]['coin'])
```

Or pass credentials directly instead of relying on the environment:

```python
from typed_bybit import Bybit

async with Bybit.new(api_key='...', api_secret='...') as client:
  ...
```

`Bybit.new()` is authenticated by default — it raises `AuthError` if neither the environment
nor the constructor supplies a key and secret. Pass `public=True` for the credential-free
client, restricted to `client.http.market` and the public WebSocket streams:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  ticker = await client.http.market.tickers(category='spot', symbol='BTCUSDT')
```

One key/secret pair authenticates every signed transport on the client: HTTP endpoints under
`client.http.trade`, `.position`, `.account`, `.asset`, and the rest of the authenticated REST
tree, the signed `private` WebSocket connection (`client.ws.private`), and the signed WS Trade
order-entry connection (`client.ws.trade`).

See [Configuration](reference/configuration.md) for `region`, `testnet`, and the rest of the
constructor's arguments.
