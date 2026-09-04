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

`client.crypto_ws` is a separate connection: one `authenticate` command, then every notification your account is entitled to arrives unprompted, with no subscribe/unsubscribe protocol of its own. Mint the token the same way `trading_ws` does, from `client.http_client.credentials`:

```python
from typed_bit2me import Bit2Me
from typed_bit2me.core.auth import mint_ws_token

async with Bit2Me.new() as client:
  assert client.http_client.credentials is not None
  token = await mint_ws_token(client.http_client.credentials, base_url=client.http_client.base_url)
  async with client.crypto_ws as crypto:
    await crypto.authenticate(payload={'token': token})
    async for notification in crypto.notifications():
      print(notification['type'], notification['payload'])
```

`authenticate` gets no reply frame of its own -- silence means it worked, and every notification the account is entitled to starts arriving on this same connection once it succeeds. `notifications()` yields `AccountNotification`, a real, typed union discriminated by each message's own `type` field, one variant per notification type Bit2Me documents (deposits, withdrawals, order fills, KYC status changes, ...) -- a handful whose upstream docs sketch only field names, with no live example to type against yet, keep their inner `payload` permissive rather than guessing a shape.
