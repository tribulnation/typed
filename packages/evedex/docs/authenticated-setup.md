# Authenticated Setup

EVEDEX accounts are Ethereum wallets. The client accepts two credentials, and which one you
need depends on what you want to do:

| Credential | Variable (production) | Unlocks |
| --- | --- | --- |
| Wallet private key | `EVEDEX_PRIVATE_KEY` | Everything: account reads, trading, private streams, the Auth service |
| API key | `EVEDEX_API_KEY` | Private Exchange REST reads only (balances, positions, orders, fills) |

## Read-Only: API Key

Create a key in the EVEDEX web app under **Settings → API → Create API Key**. It is sent as
the `X-API-Key` header and only works on the Exchange service's private reads: it cannot
sign orders, open private WebSocket channels, or call the Auth service.

```bash
# .env
EVEDEX_API_KEY="your_api_key"
```

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  positions = await client.exchange.positions.list()
  orders = await client.exchange.orders.opened()
```

## Full Access: Wallet Private Key

Set the private key of the wallet that owns your EVEDEX account. `EVEDEX_ADDRESS` is
optional; when set, the client checks it matches the key. The key must be the account's
own externally owned address, not a smart-account wallet.

```bash
# .env
EVEDEX_PRIVATE_KEY="0x..."
EVEDEX_ADDRESS="0x..."  # optional
```

With a private key the client handles two signing layers for you:

1. **Session (Sign-In with Ethereum).** On the first private call it fetches a nonce,
   signs an EIP-4361 message and receives a short-lived JWT access token plus a refresh
   token. It refreshes the access token before it expires and signs in again if a refresh
   is refused. `client.auth.session.logout()` and `revoke()` end the session explicitly.
2. **EIP-712 action signatures.** Order placement and replacement, position close, TP/SL
   create/update and withdrawal carry a wallet signature in the request body. The client
   builds the typed data, adds the chain id and a fresh order id, and signs it. Cancels and
   leverage changes are not signed.

If both variables are set, Exchange REST calls authenticate with the API key and the private
key still signs actions, opens the session for the Auth service, and opens private channels.

A wallet that has never used EVEDEX has no exchange account yet; private Exchange calls
then raise `AuthError` (`user_not_found_error`). Create it once:

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  user = await client.exchange.account.create()
  print(user.get('exchangeId'))
```

## Managing API Keys

With the private key you can manage API keys from code:

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  issued = await client.auth.api_keys.create('read-only bot', scopes=['exchange'])
  print(issued['apiKey'])  # shown only now and on regenerate
  keys = await client.auth.api_keys.list()
  await client.auth.api_keys.delete(issued['id'])
```

## Demo Environment

`Evedex.new(env='demo')` targets `evedex.io`, with its own accounts and the `EVEDEX_DEMO_`
prefix: `EVEDEX_DEMO_PRIVATE_KEY`, `EVEDEX_DEMO_API_KEY`, `EVEDEX_DEMO_ADDRESS`. Demo
instrument names carry a suffix (`BTCUSD:DEMO`). Explicit arguments override the
environment variables:

```python
from typed_evedex import Evedex

async with Evedex.new(env='demo', private_key='0x...') as client:
  status = await client.exchange.account.faucet.check()
```
