# Environment Variables

| Variable | Required for | Description |
|---|---|---|
| `KRAKEN_API_KEY` | private REST calls, `streams.private`, `trading_ws` | Kraken API key. |
| `KRAKEN_PRIVATE_KEY` | private REST calls, `streams.private`, `trading_ws` | Kraken private key, used to sign requests. |

Both are read by `Kraken.new()` when `api_key`/`private_key` aren't passed directly, and
are unused entirely when the client is built with `public=True`. See
[API Keys Setup](../api-keys.md) for where to generate them.
