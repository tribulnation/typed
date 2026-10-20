# Environment Variables

`Grvt.new()` reads credentials from environment variables when they are not passed as
arguments. Each environment has its own prefix, so a testnet credential is never used
against production.

| Variable | Used for |
| --- | --- |
| `GRVT_API_KEY` | API key; exchanged for the session every authenticated call uses |
| `GRVT_PRIVATE_KEY` | the API key's signer private key; signs `create_order`, `bulk_orders`, `transfer`, `withdrawal` and `set_derisk_mm_ratio` |
| `GRVT_TRADING_ACCOUNT_ID` | optional default trading sub-account id |

| `env=` | Prefix | Example |
| --- | --- | --- |
| `'prod'` (default) | `GRVT_` | `GRVT_API_KEY` |
| `'testnet'` | `GRVT_TESTNET_` | `GRVT_TESTNET_API_KEY` |
| `'staging'` | `GRVT_STAGING_` | `GRVT_STAGING_API_KEY` |

```bash
# .env for testnet
GRVT_TESTNET_API_KEY="your_api_key"
GRVT_TESTNET_PRIVATE_KEY="0xyour_signer_private_key"
GRVT_TESTNET_TRADING_ACCOUNT_ID="your_sub_account_id"
```

## Which Are Required

1. With `public=True`, none: `client.market`, `client.market_streams`, and the public edge
   calls `investment_strategies` and `rhino_chain_id` work; every other call raises
   `AuthError`.
2. Otherwise at least the API key or the private key must be set, or `Grvt.new()` raises
   `AuthError`. With only the private key, the client logs in as the account's funding
   wallet (see [Wallet Login](../api-keys.md#wallet-login)).
3. The signed calls also need the private key: `create_order`, `bulk_orders`, `transfer`,
   `withdrawal` and `set_derisk_mm_ratio`. Without it they raise `AuthError`. A `bulk_orders`
   batch that only cancels is not signed, and neither is a call you pass a complete,
   pre-signed `signature`.
4. Without a trading account id, trading calls use the sub-account a trading-account key is
   scoped to. An account-level key has none, and neither has a wallet login: a trading call
   that leaves `sub_account_id` out then raises `AuthError` (no default trading sub-account).
   Pass `sub_account_id` to the call, or set a default: `GRVT_TRADING_ACCOUNT_ID` when
   credentials come from the environment, `Grvt.new(trading_account_id=...)` when you pass
   the keys as arguments.

## Arguments Or Environment

Credentials come from one source only, so a key is never mixed with another account's:

1. Pass `api_key` or `private_key` to `Grvt.new()`, and nothing is read from the
   environment, not even the trading account id. Leave `trading_account_id` out to use the
   sub-account a trading-account key is scoped to.
2. Pass neither, and all three variables are read. An explicit `trading_account_id` still
   overrides `GRVT_TRADING_ACCOUNT_ID`.

The client never reads a `.env` file itself; load it with a tool such as `python-dotenv`.
