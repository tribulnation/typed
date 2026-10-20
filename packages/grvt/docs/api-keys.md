# API Keys Setup

GRVT authenticated calls need two secrets:

1. an **API key**, which the client exchanges for a session cookie (login and refresh are
   automatic), and
2. the **signer private key** the API key is tagged with, which signs (EIP-712) the calls
   GRVT requires a signature on: `create_order`, `bulk_orders`, `transfer`, `withdrawal` and
   `set_derisk_mm_ratio`. Signing is local: the key never leaves your process.

Market data needs neither: build the client with `public=True`.

## Create API Credentials

Create a key on the GRVT exchange's API keys page ([production](https://grvt.io/exchange/account/api-keys),
[testnet](https://testnet.grvt.io/exchange/account/api-keys)). When creating it, either supply
your own signer address or let the UI generate a keypair. A generated private key is shown
only once, so store it right away.

A key is either trading-account level, scoped to one trading sub-account (trade only), or
account level, with optional transfer and withdrawal permissions. IP whitelisting is
optional.

## Environment Variables

`Grvt.new()` reads credentials for the environment it connects to, each under its own
prefix:

```bash
# testnet: Grvt.new(env='testnet')
GRVT_TESTNET_API_KEY="your_testnet_api_key"
GRVT_TESTNET_PRIVATE_KEY="0xyour_testnet_signer_private_key"
GRVT_TESTNET_TRADING_ACCOUNT_ID="your_testnet_sub_account_id"  # optional, see below

# production: Grvt.new()
GRVT_API_KEY="your_api_key"
GRVT_PRIVATE_KEY="0xyour_signer_private_key"
GRVT_TRADING_ACCOUNT_ID="your_sub_account_id"  # optional, see below
```

Staging uses the `GRVT_STAGING_` prefix with `env='staging'`. A client reads only its own
environment's variables, so a testnet key is never sent to production.

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  summary = await client.trading.account_summary()
  print(summary['total_equity'])
```

The `TRADING_ACCOUNT_ID` variable is the sub-account used when a trading call leaves
`sub_account_id` out. Unset, a trading-account key uses its own sub-account. An account-level
key has none: set the variable (or pass `trading_account_id` to `Grvt.new()`), or pass
`sub_account_id` to each trading call, since a trading call that leaves it out with no
default raises `AuthError`.

## Direct Usage

```python
from typed_grvt import Grvt

async with Grvt.new(
  api_key='your_api_key',
  private_key='0xyour_signer_private_key',
  trading_account_id='your_sub_account_id',
) as client:
  print(await client.sub_account_id())
```

Passing either key reads nothing from the environment (see
[Environment Variables](reference/env-vars.md)). Without `private_key`, reads still work, but
`create_order`, `bulk_orders`, `transfer`, `withdrawal` and `set_derisk_mm_ratio` raise
`AuthError` because they cannot be signed (a `bulk_orders` batch that only cancels is not
signed).

## Wallet Login

With a private key and no API key, the client logs in by signing GRVT's wallet login
message instead, and the same key signs the calls above:

```python
from typed_grvt import Grvt

async with Grvt.new(
  private_key='0xyour_funding_wallet_private_key',
  trading_account_id='your_sub_account_id',
) as client:
  print(await client.trading.funding_account_summary())
```

GRVT accepts only the account's funding wallet here: an API key's signer key is refused at
login with `AuthError` (`wallet address not registered`). Without an API key there is no
sub-account to default to, so set `trading_account_id`. Prefer an API key where you can: it
can be limited to the permissions your code needs, and revoked on its own.

## Security Notes

- never commit credentials to git
- give each key only the permissions it needs, and whitelist its IPs
- try new code on testnet first
