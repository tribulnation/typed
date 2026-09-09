# Environment Variables

Typed Coinbase reads these when not passed directly to `Coinbase.new()`:

```bash
COINBASE_API_KEY_NAME="organizations/{org_id}/apiKeys/{key_id}"
COINBASE_PRIVATE_KEY="-----BEGIN EC PRIVATE KEY-----..."
```

Both come from a CDP API Key created in the [CDP Portal](https://portal.cdp.coinbase.com/). `COINBASE_PRIVATE_KEY` is either the EC (P-256) PEM export, or the portal's base64-encoded Ed25519 seed — the format is detected automatically, no configuration needed.

Neither is required for a `public=True` client, which only reaches `app.advanced_trade.http.products.public` and the `app.advanced_trade.streams.market_data` WebSocket channels.

See [API Keys Setup](../api-keys.md) for how to create these.

## Coinbase Exchange (Optional, Institutional)

Coinbase Exchange is a separate product with its own credential — a key/secret/passphrase triple, unrelated to the CDP API Key above:

```bash
COINBASE_EXCHANGE_API_KEY="..."
COINBASE_EXCHANGE_API_SECRET="..."
COINBASE_EXCHANGE_PASSPHRASE="..."
```

All three are optional: `exchange_public` defaults to `True`, so `client.exchange` is public-only unless these are set (or passed directly) and `exchange_public=False` is requested explicitly. See [Exchange API Keys Setup](../exchange-api-keys.md) for how to create these.
