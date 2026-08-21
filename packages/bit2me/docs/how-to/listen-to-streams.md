# Listen To Streams

Bit2Me exposes two independent WebSocket connections, `client.trading_ws` and `client.crypto_ws`. Both connect lazily on first use, so nothing needs opening explicitly, but wrapping the one you use in its own `async with` gives you deterministic cleanup, and for `client.trading_ws` it's also what authenticates the connection when the client holds credentials.

## Public Order Book And Trades

`client.trading_ws` needs no credentials for its public channels:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  async with client.trading_ws as trading:
    async with trading.order_book(symbol='BTC/EUR') as stream:
      async for update in stream:
        print(update.get('bids', [])[:1], update.get('asks', [])[:1])
```

`trading.public_trades(symbol='BTC/EUR')` streams every executed trade on a symbol the same way.

## Your Own Orders, Trades, And Balance

The same connection carries private channels once authenticated. Build the client with `Bit2Me.new()`, and Bit2Me authenticates the socket for you on `__aenter__`:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  async with client.trading_ws as trading:
    async with trading.my_orders() as stream:
      async for update in stream:
        print(update['id'], update['status'])
```

`trading.my_trades()`, `trading.my_balance()`, and `trading.my_working_capital()` subscribe the same way. Pass `symbol=` to `my_orders`/`my_trades` to filter to one market.

## Account Notifications

`client.crypto_ws` is a separate connection: one `authenticate` frame, then every notification your account is entitled to arrives unprompted, with no subscribe/unsubscribe protocol. Mint the token the same way `trading_ws` does, from `client.http.credentials`:

```python
from typed_bit2me import Bit2Me
from typed_bit2me.core.auth import mint_ws_token

async with Bit2Me.new() as client:
  assert client.http.credentials is not None
  token = await mint_ws_token(client.http.credentials, base_url=client.http.base_url)
  async with client.crypto_ws as crypto:
    await crypto.authenticate(token=token)
    async for notification in crypto.notifications():
      print(notification['type'], notification['payload'])
```

Each notification is a permissive `dict` carrying at least `type` and `payload`. Bit2Me documents dozens of notification types (deposits, withdrawals, order fills, KYC status changes, ...) but only sketches each payload's shape, not a full schema.
